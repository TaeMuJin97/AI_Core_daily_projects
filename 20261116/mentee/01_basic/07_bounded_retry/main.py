"""
==============================================================================
[실습 보고서: Day 21 실습 07 - 실패 분류 및 제한된 재시도 제어 (07_bounded_retry/main.py)]
1. 핵심 아키텍처 개념:
   - Bounded Retry (제한된 재시도): 무한 반복(while True)으로 인한 API 비용 폭발을 막기 위해
     튜플 (1, 2) 순회로 '최초 1회 + 형식 수정 1회 = 최대 2회'까지만 물리적으로 허용함.
   - Error Triage (오류 분류별 분기):
     * 형식 오류 (json_error, schema_error) -> 1회 수정 요청(repair_prompt) 후 재시도
     * 내용/규칙 위반 (unknown_source, status_rule 등) -> 재시도해도 없는 근거가 생기지 않으므로 즉시 중단(break)
     * 정상 정보 부족 (insufficient_context, error=None) -> 실패가 아닌 정상 결과이므로 1회에 즉시 종료
   - First-Class Function (일급 함수/의존성 주입): generate와 validate 함수를 매개변수로 받아,
     오늘의 Fixture 테스트와 내일의 실제 LLM API 호출에 동일한 제어 코드를 재사용함.
   - SHA-256 해시 추적 (sha_text): 프롬프트 변경 여부(1차 원본 vs 2차 수정본)를 해시 지문으로 증명함.
==============================================================================
"""
"""Day21 실습 07: 실패 분류·최대 2회. 실행: python main.py"""
from pathlib import Path
import sys

# Path(__file__).resolve().parent: 현재 실행 중인 main.py 파일의 절대 경로 폴더(07_bounded_retry)
HERE = Path(__file__).resolve().parent
# parents[1]: 두 단계 상위 폴더(mentee 루트 폴더)를 찾아 sys.path에 등록하여 coursekit 패키지를 불러옴
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

# sha_text: 문자열을 넣으면 고유한 SHA-256 해시값(지문)을 반환하는 유틸리티 함수
from coursekit.io import DATA, read_json, write_json, sha_text, run

# 기준: Day21 PPT 56~63장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.
from coursekit.retry import run_fixture_scenarios


def repair_prompt(original, error):
    # TODO D21-07-B01: 허용한 형식 오류만 안전한 한 문장 요약으로 수정 요청을 만드세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: unknown_source는 자동 형식 수정 요청을 만들지 않습니다.
    # BEGIN D21-07-B01

    # [핵심 개념 1: 화이트리스트(Allowlist) 딕셔너리 설계]
    # - 왜 모델이 뱉은 깨진 원문(raw_text)이나 파이썬 에러(Traceback)를 그대로 프롬프트에 안 넣을까?
    #   1) 깨진 출력이나 외부 데이터 안에 악성 명령(Prompt Injection)이 섞여 재주입될 위험 방지
    #   2) 불필요하게 긴 에러 로그로 인한 입력 토큰(Context Budget) 낭비 방지
    # - 따라서 오직 복구 가능한 두 가지 '형식 오류(json_error, schema_error)'만 키(Key)로 등록하고,
    #   미리 검증된 안전하고 짧은 한 문장 지시문(Value)만 매핑해 둡니다.
    safe = {
        "json_error": "코드 블록이나 부연 설명 없이 문법에 맞는 JSON 객체 하나만 출력하세요.",
        "schema_error": "status, answer, source_ids, missing_information 네 필수 필드와 자료형·길이 제한을 지키세요.",
    }

    # [방어 로직 (Guard Clause)]
    # - 만약 error가 "unknown_source"(없는 출처 인용)나 "status_rule"(상태 모순)이라면
    #   safe 딕셔너리에 없으므로 즉시 ValueError 예외를 발생시켜 잘못된 재시도 생성을 원천 차단합니다.
    if error not in safe:
        raise ValueError("형식 오류만 수정 요청을 만듭니다")

    # [프롬프트 불변성(Immutability) 유지 및 수정 요청 덧붙이기]
    # - 원본 프롬프트(original: 질문 + 지식 문맥 + 출력 계약)를 훼손하지 않고 그대로 유지한 채,
    #   맨 마지막 줄에 "\n[수정 요청] "과 해당 오류의 안전 요약문(safe[error])만 이어 붙입니다.
    repaired = original + "\n[수정 요청] " + safe[error]
    # 이전 원문 전체, traceback, 비밀 값은 붙이지 않습니다.
    # END D21-07-B01
    return repaired


def run_with_retry(generate, prompt, validate):
    # TODO D21-07-B02: 최초 1회+수정 1회까지만 반복하고 통과하지 못하면 None을 반환하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 호출 수가 최대 2. 정상 정보 부족도 1회에 종료.
    # 핵심: 성공 반환은 자동 구조·참조 통과일 뿐입니다. 근거를 맞게 읽었는지 사람 검토가 남습니다.
    # BEGIN D21-07-B02

    # [핵심 개념 2: 일급 함수(First-Class Function) 매개변수]
    # - generate와 validate는 일반 데이터가 아니라 '함수(Function)'를 인자로 넘겨받은 것입니다!
    #   * generate(prompt): 프롬프트를 받아 응답 문자열(raw)을 돌려주는 함수 (현재는 Fixture 공급기, 내일은 실제 API 함수)
    #   * validate(raw): 응답 문자열을 검사해 (통과객체 obj, 에러코드 error) 튜플을 돌려주는 함수

    # [시도별 블랙박스 기록장 초기화]
    # - 2차 시도에서 성공하더라도 1차 시도에서 실패했던 사실을 지우지 않고 모두 누적 기록하기 위한 리스트입니다.
    history = []

    # [핵심 개념 3: 유한 루프 (for attempt in (1, 2))]
    # - while 문을 쓰지 않고 튜플 (1, 2)를 순회하여 물리적으로 최대 2번(attempt=1, attempt=2)만 실행되게 강제합니다.
    for attempt in (1, 2):
        # 1) 생성 함수 호출: 현재 prompt를 넣어 원문 응답 문자열(raw)을 받음
        raw = generate(prompt)

        # 2) 검증 함수 호출 및 튜플 언패킹(Tuple Unpacking):
        #    통과 시 -> obj=KnowledgeAnswer 객체, error=None
        #    실패 시 -> obj=None, error="json_error" 등 오류 코드 문자열
        obj, error = validate(raw)

        # 3) 실행 이력(Audit Log) 기록:
        #    sha_text(prompt)는 현재 프롬프트의 SHA-256 해시 지문을 남깁니다.
        #    1차 시도(원본 prompt)와 2차 시도(repair_prompt가 적용된 prompt)의 해시값이 달라지는 것을 확인할 수 있습니다.
        history.append(
            {
                "attempt": attempt,
                "error": error,
                "raw_text": raw,
                "prompt_sha256": sha_text(prompt),
            }
        )

        # [분기 1: 검증 통과 시 즉시 종료 (Early Return)]
        # - error가 None이라는 것은 JSON 문법, Pydantic 스키마, 참조/상태 규칙을 모두 통과했다는 뜻입니다.
        # - 주의: 정상적인 정보 부족(status="insufficient_context") 응답도 규칙을 지켰다면 error가 None이므로,
        #   재시도하지 않고 여기서 1회 만에 즉시 (obj, history)를 반환하며 끝납니다!
        if error is None:
            return obj, history

        # [분기 2: 재시도 불가 오류이거나 최대 횟수(2회) 도달 시 즉시 중단 (Break)]
        # - 조건 A (error not in ("json_error", "schema_error")):
        #   출처 위반("unknown_source"), 상태 모순("status_rule") 등은 형식 수정으로 고쳐지지 않으므로 1회차에 바로 중단!
        # - 조건 B (attempt == 2):
        #   이미 2차(수정) 시도까지 했는데도 또 오류가 났다면 더 이상 repair_prompt를 만들지 않고 즉시 루프 탈출!
        if error not in ("json_error", "schema_error") or attempt == 2:
            break

        # [분기 3: 1차 시도에서 형식 오류(json_error, schema_error)가 발생한 경우에만 프롬프트 수선]
        # - 위 두 if문에 걸리지 않았다는 것은 "현재 attempt == 1이고, error가 json_error 또는 schema_error"라는 뜻입니다.
        # - 다음 루프(attempt == 2)에 들어가기 직전에 [수정 요청] 문구가 붙은 새 프롬프트로 교체합니다.
        prompt = repair_prompt(prompt, error)

    # [최종 실패 반환: 실패를 성공으로 숨기지 않음]
    # - break로 루프를 빠져나왔다면 끝내 검증을 통과하지 못한 상태입니다.
    # - 통과한 객체 자리에는 명시적으로 None을 넣고, 그동안의 실패 과정이 담긴 history를 함께 반환합니다.
    return None, history
    # END D21-07-B02


def main():
    fixtures = read_json(DATA / "validation_fixtures.json")
    # TODO D21-07-B03: 네 fixture 순서의 호출 수 2·2·1·1을 확인하고 기록하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 복구 성공·연속 실패·규칙 중단·부족 정상 종료 네 경우.
    # BEGIN D21-07-B03

    # [핵심 개념 4: 콜백 함수(runner=run_with_retry) 전달을 통한 시나리오 시뮬레이션]
    # - 우리가 위에서 만든 run_with_retry 함수 자체(괄호 없이 이름만!)를 runner 인자로 넘겨주면,
    #   run_fixture_scenarios가 내부에서 4가지 대표 시나리오를 차례대로 실행해 결과를 돌려줍니다.
    results = run_fixture_scenarios(fixtures, runner=run_with_retry)

    # [리스트 컴프리헨션(List Comprehension)으로 각 시나리오의 호출 횟수(calls) 추출]
    # - results 안의 4개 시나리오 결과 딕셔너리에서 "calls"(총 generate 호출 횟수) 값만 뽑아 리스트로 만듭니다.
    #   1) 시나리오 1 (1차 형식 오류 -> 2차 복구 성공): 2회 호출
    #   2) 시나리오 2 (1차 형식 오류 -> 2차 또 형식 오류로 최종 실패): 2회 호출
    #   3) 시나리오 3 (1차 unknown_source 규칙 위반 -> 즉시 중단): 1회 호출
    #   4) 시나리오 4 (1차 정상 insufficient_context -> 즉시 통과 종료): 1회 호출
    calls = [r["calls"] for r in results]

    # 4개 시나리오의 호출 횟수가 정확히 [2, 2, 1, 1]과 일치하는지 단언(assert) 검증
    assert calls == [2, 2, 1, 1]

    # 이 결과는 실제 LLM의 복구율이 아니라 로컬 제어 흐름(fixture)을 검증한 결과이므로 source_mode="fixture"로 명시해 저장
    write_json(
        HERE / "outputs" / "retry_results.json",
        {"source_mode": "fixture", "results": results},
    )
    # END D21-07-B03
    print("[07] 제어 흐름만 검증했습니다. 실제 모델 복구율은 측정하지 않았습니다.")


if __name__ == "__main__":
    run(main)