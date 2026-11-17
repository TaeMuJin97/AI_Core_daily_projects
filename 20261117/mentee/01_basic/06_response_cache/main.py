"""
==============================================================================
[실습 보고서: Day 22 실습 06 - 사람 승인 응답 캐시(Response Cache)와 무효화 (main.py)]
1. 실험 목적:
   - 동일한 조건의 요청에 대해 이미 검증·승인된 최종 답변을 재사용(App Response Cache)하여
     불필요한 외부 API 호출(new_api_send_count = 0)과 비용·지연 시간을 줄임.
   - 단, 잘못된 답변이나 문맥이 바뀐 과거 답변이 오염되어 반환되지 않도록 엄격한 캐시 키(SHA-256)
     생성 규칙과 읽기 시점 재검증(checkpoint_cache)을 구현함.
2. 핵심 아키텍처 및 checkpoint_cache(read_cache) 심층 해부:
   - 왜 질문(question)만으로 캐시 키를 만들면 안 되는가? (D22-06-B01):
     같은 질문("파일을 어디에 보관하나요?")이라도 1) 참조한 지식 본문(content), 2) 사용한 모델(model),
     3) 사용자 권한 범위(scope), 4) 프롬프트 지시문(instructions), 5) 출력 스키마(format),
     6) 로컬 검증기 버전(validator_version) 중 하나라도 바뀌면 결과도 달라져야 함.
     따라서 이 6가지를 모두 묶어 키를 정렬한 뒤 SHA-256 해시(digest)를 계산함. (단, API 키는 절대 제외!)
   - ★ checkpoint_cache(coursekit.cache.read_cache)의 6단계 방어선 (D22-06-B02):
     캐시 키가 일치(Key Hit)했다고 해서 무조건 저장된 답변을 반환하면 보안·품질 사고가 남.
     checkpoint_cache는 읽기 시점에 다음 6가지를 순서대로 다시 검사하며, 하나라도 실패하면 None(Cache Miss)을 반환함:
       ① 엔트리 존재 확인: cache.get(key)가 없으면 즉시 None 반환.
       ② TTL(Time To Live) 만료 확인: 현재 시각(now) >= entry["expires_at"] 이면 만료로 판단해 None 반환.
       ③ 사람 근거 승인 확인: entry["human_approved"]가 True가 아니면(사람이 review.py로 승인 안 함) None 반환.
       ④ 권한 범위(scope) 및 실행 출처(expected_source) 교차 오염 방지:
          다른 조직/권한(scope)의 캐시이거나, 모의 실행(simulated) 결과를 실제 호출(api_live)에서 쓰려 하면 차단.
       ⑤ 현재 문맥(provided_ids) 및 현재 검증기 규칙 재실행:
          저장된 원문(entry["raw"])을 꺼내 현재 시점의 로컬 검증기(inspect_answer / validate_answer)에 다시 통과시켜,
          만약 그사이 검증 규칙이나 허용 출처 ID(provided_ids)가 바뀌었으면 즉시 차단.
       ⑥ 원래 실행 추적(Provenance) 및 0회 전송 기록 반환:
          모든 관문을 통과하면 source_mode="app_cache", origin_run_id=원래_실행_ID, new_api_send_count=0을 담아 반환.
==============================================================================
"""
"""Day22 · 승인 응답 캐시 | PPT 47~52 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from copy import deepcopy
from coursekit.support import parse_args, guarded, cache_lab
from coursekit.io import write_json, digest
from coursekit.request import OUTPUT_FORMAT, build_request as checkpoint_request
from coursekit.cache import read_cache as checkpoint_cache


def key_of(request, scope, validator_version="day21-v1"):
    # TODO D22-06-B01: 질문뿐 아니라 모델·전체요청·Schema·검증버전·scope로 캐시키를 만드세요.
    # 입력·완료 기준: API키는포함하지않습니다. 전체본문이키에들어가야같은ID의내용변경도감지합니다.
    # BEGIN D22-06-B01

    # [핵심 포인트 1: 결과에 영향을 주는 모든 결정 조건(Basis)을 묶어 SHA-256 해시 생성]
    # - request 안에는 이미 instructions와 직렬화된 user input(질문 + 선택된 지식의 id·title·content 전체)이 들어있습니다.
    # - 따라서 지식 ID(예: 103)가 그대로여도 안의 본문(content)이 한 글자라도 수정되면 request가 달라지고,
    #   digest(basis)가 계산하는 SHA-256 해시값도 완전히 다른 값으로 바뀝니다(자동 캐시 무효화).
    # - text.format(출력 스키마)은 request["text"]["format"]에서 꺼내며, 없으면 기본 OUTPUT_FORMAT을 참조합니다.
    fmt = (request.get("text") or {}).get("format") if isinstance(request.get("text"), dict) else None
    basis = {
        "scope": scope,
        "model": request.get("model"),
        "request": request,
        "format": fmt if fmt is not None else OUTPUT_FORMAT,
        "validator_version": validator_version,
    }
    key = digest(basis)  # digest(basis): 딕셔너리 키를 정렬(sort_keys=True)한 JSON의 SHA-256 해시 문자열
    return key
    # END D22-06-B01


def approved_cache(cache, key, now, provided_ids, *, expected_source, scope):
    # TODO D22-06-B02: 현재문맥·실행출처·scope와함께 제공된 안전한캐시검사를 호출하세요.
    # 입력·완료 기준: 만료·미승인·현재출처불일치는미스입니다. 승인하려면tools/review.py로사람이기록합니다.
    # BEGIN D22-06-B02

    # [핵심 포인트 2: checkpoint_cache(coursekit.cache.read_cache)를 통한 읽기 시점 6중 검증]
    # - 단순히 cache[key]로 꺼내 쓰지 않고 checkpoint_cache에 위임하는 이유:
    #   1) key가 존재하는지 확인
    #   2) TTL 유효기간(now < expires_at)이 남았는지 확인
    #   3) 사람이 근거를 검토해 승인(human_approved == True)한 answered 결과인지 확인
    #   4) 요청한 권한 범위(scope) 및 실행 출처(expected_source: api_live vs simulated)가 일치하는지 확인
    #   5) 저장된 응답 원문(raw)이 현재 제공된 지식 ID 집합(provided_ids) 및 로컬 검증 규칙을 여전히 통과하는지 재검증
    # - 위 조건 중 하나라도 어긋나면 checkpoint_cache는 None(Cache Miss)을 반환합니다.
    #   이때 임의로 가짜 답변을 만들어 넣지 않고 None 그대로 반환해야 상위 루프가 명확히 Miss로 기록합니다.
    cached = checkpoint_cache(
        cache,
        key,
        now,
        provided_ids,
        expected_source=expected_source,
        scope=scope,
    )
    return cached
    # END D22-06-B02


def compare_context_keys():
    # TODO D22-06-B03: 같은ID의본문변경이캐시키를바꾸는지확인하세요.
    # 입력·완료 기준: 이키비교는전송0회의모의검사입니다. 실제재사용은먼저생성·사람승인후reuse명령으로확인합니다.
    # BEGIN D22-06-B03

    # [핵심 포인트 3: 지식 ID가 같아도 본문(content)이 바뀌면 캐시 키가 달라짐을 증명]
    # - H01 질문과 선택 지식(ID 103)으로 첫 번째 요청(first)을 만들고 캐시 키(before_key)를 뽑습니다.
    # - 원본 데이터가 훼손되지 않게 deepcopy(selected)로 깊은 복사본(changed)을 만든 뒤,
    #   ID는 103 그대로 둔 채 본문(changed[0]["content"]) 뒤에 문장을 덧붙여 두 번째 요청(second)을 만듭니다.
    # - 두 요청의 SHA-256 캐시 키를 비교하면 서로 다른 해시가 나와(same_key == False) 이전 캐시가 무효화됨을 확인합니다.
    from coursekit.io import input_parts
    from coursekit.config import load_settings

    settings = load_settings("simulated")
    case, selected, instructions = input_parts("H01")
    model = settings.models["fast"]
    scope = getattr(settings, "scope", "classroom-demo")

    first = checkpoint_request(model, instructions, case["question"], selected)
    changed = deepcopy(selected)  # 원본 JSON 파일이나 메모리의 selected 리스트는 바꾸지 않습니다.
    changed[0]["content"] += " 실행 환경도 함께 적습니다."
    second = checkpoint_request(model, instructions, case["question"], changed)

    before_key = key_of(first, scope)
    after_key = key_of(second, scope)
    return {
        "case_id": case["case_id"],
        "knowledge_id": selected[0]["id"],
        "before_key": before_key,
        "after_key": after_key,
        "same_key": before_key == after_key,
        "invalidated": before_key != after_key,
        "new_api_sends": 0,
    }
    # END D22-06-B03


def main():
    args = parse_args(HERE)
    write_json(args.output_dir / "cache_key_checks.json", compare_context_keys())
    result = cache_lab(args, key_builder=key_of, cache_reader=approved_cache)


if __name__ == "__main__":
    guarded(main)