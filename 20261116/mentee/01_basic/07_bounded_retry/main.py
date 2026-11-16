"""
==============================================================================
[실습 보고서: Day 21 실습 07 - 실패 분류 및 제한된 재시도 제어 (07_bounded_retry/main.py)]
1. 실험 목적: 모든 검증 실패를 무조건 반복 호출하지 않고, 형식 오류(json_error, schema_error)만
              1회 수정 요청하여 최대 2회(최초 1회 + 수정 1회) 안에서 안전하게 제어 및 중단함.
2. 핵심 포인트:
   - 안전한 수정 프롬프트 조립 (D21-07-B01): 이전 실패 원문 전체나 파이썬 traceback을 붙이지 않고,
     json_error와 schema_error에 대해서만 한 문장 요약 안내([수정 요청])를 추가함.
   - 제한된 재시도 루프 (D21-07-B02):
     1) error is None이면(정상 answered 및 정상 insufficient_context 포함) 1회에 즉시 (obj, history) 반환.
     2) unknown_source 등 참조/상태 규칙 위반이거나 2차 시도까지 실패하면 즉시 중단하고 (None, history) 반환.
     3) 1차 시도에서 형식 오류가 났을 때만 repair_prompt를 거쳐 2차 시도를 수행함.
   - 시나리오별 호출 수 검증 (D21-07-B03): 복구 성공(2회), 연속 실패(2회), 규칙 위반 중단(1회),
     정보 부족 정상 종료(1회)의 호출 수 [2, 2, 1, 1]을 확인하고 모든 시도 이력을 보존함.
==============================================================================
"""
"""Day21 실습 07: 실패 분류·최대 2회. 실행: python main.py"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, sha_text, run

# 기준: Day21 PPT 56~63장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.
from coursekit.retry import run_fixture_scenarios


def repair_prompt(original, error):
    # TODO D21-07-B01: 허용한 형식 오류만 안전한 한 문장 요약으로 수정 요청을 만드세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: unknown_source는 자동 형식 수정 요청을 만들지 않습니다.
    # BEGIN D21-07-B01
    safe = {
        "json_error": "코드 블록이나 부연 설명 없이 문법에 맞는 JSON 객체 하나만 출력하세요.",
        "schema_error": "status, answer, source_ids, missing_information 네 필수 필드와 자료형·길이 제한을 지키세요.",
    }
    if error not in safe:
        raise ValueError("형식 오류만 수정 요청을 만듭니다")
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
    history = []
    for attempt in (1, 2):
        raw = generate(prompt)
        obj, error = validate(raw)
        history.append(
            {
                "attempt": attempt,
                "error": error,
                "raw_text": raw,
                "prompt_sha256": sha_text(prompt),
            }
        )
        if error is None:
            return obj, history
        if error not in ("json_error", "schema_error") or attempt == 2:
            break
        prompt = repair_prompt(prompt, error)
    return None, history
    # END D21-07-B02


def main():
    fixtures = read_json(DATA / "validation_fixtures.json")
    # TODO D21-07-B03: 네 fixture 순서의 호출 수 2·2·1·1을 확인하고 기록하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 복구 성공·연속 실패·규칙 중단·부족 정상 종료 네 경우.
    # BEGIN D21-07-B03
    results = run_fixture_scenarios(fixtures, runner=run_with_retry)
    calls = [r["calls"] for r in results]
    assert calls == [2, 2, 1, 1]
    write_json(
        HERE / "outputs" / "retry_results.json",
        {"source_mode": "fixture", "results": results},
    )
    # END D21-07-B03
    print("[07] 제어 흐름만 검증했습니다. 실제 모델 복구율은 측정하지 않았습니다.")


if __name__ == "__main__":
    run(main)