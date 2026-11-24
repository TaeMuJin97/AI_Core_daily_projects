"""Day27 강의 실습. 실행은 역할 폴더에서 Python으로 실행합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROLE_ROOT = next(p for p in HERE.parents if (p / "coursekit").is_dir())
sys.path.insert(0, str(ROLE_ROOT))

import argparse
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report

# -----------------------------------------------------------------------------
# 2. 진단 단계 상수 및 단계별 처방 매핑 (Magic String 방지)
#    - 파이프라인 순서대로 단계 이름을 상수로 정의해 오타와 불일치를 막습니다.
# -----------------------------------------------------------------------------
STAGE_REWRITE = "Query Rewrite"
STAGE_AUTH = "Authorization / Access Filter"
STAGE_VERSION = "Version / Metadata Filter"
STAGE_RETRIEVAL = "Candidate Retrieval"
STAGE_RERANK = "Reranking"
STAGE_VALIDATION = "Validation / Citation"
STAGE_HEALTHY = "No Failure (Healthy)"

ACTION_BY_STAGE: dict[str, str] = {
    STAGE_REWRITE: "대화 History에서 생략된 대상을 복원해 독립 질문(Standalone Query)으로 재작성합니다. (모호하면 재질문)",
    STAGE_AUTH: "검색 전 사용자 권한(authorized) 및 접근 제어 필터를 적용해 비인가 문서를 차단합니다.",
    STAGE_VERSION: "현재 공개 버전(current=True) 및 준비 완료(ready=True) Metadata 필터를 SQL 조회에 강제합니다.",
    STAGE_RETRIEVAL: "후보 목록에 정답이 없으므로 Reranker가 아닌 검색 범위·Category·candidate_k·Query Expansion/Multi-query 및 인덱싱을 점검합니다.",
    STAGE_RERANK: "정답이 후보에는 있으나 순위가 밀렸으므로 Cross-Encoder Reranking으로 상위 후보 순서를 재조정합니다.",
    STAGE_VALIDATION: "Context에 정답이 포함되었으나 출처·형식 규칙을 위반했으므로 Validator(receive_bundle/validate_answer) 검문과 프롬프트를 점검합니다.",
    STAGE_HEALTHY: "파이프라인 전 단계가 정상입니다. 답변 문장이 원문 사실과 일치하는지 Grounding만 최종 대조합니다.",
}


def diagnose_stage(case: dict) -> str:
    """어떤 문제가 먼저 발생했는지 위에서부터 조건을 검사합니다."""
    # BEGIN D27-01-B01
    # [흐름 이해: 파이프라인 앞 단계부터 순서대로 원인 판별하기]
    # RAG는 [질문 해석 → 권한/버전 필터 → 1차 후보 검색 → 2차 재정렬 → 최종 출처 검증] 순으로 흐릅니다.
    # 앞 단계가 실패하면 뒤 단계도 연쇄적으로 False가 되므로, 반드시 위에서부터 차례대로 검사해야 합니다.

    # 방어 코드: 입력이 dict가 아니면 즉시 명확한 예외를 발생시킵니다.
    if not isinstance(case, dict):
        raise ValueError("case는 dict 형식이어야 합니다.")

    # 1단계) 검색 전 · 질문 모호성 검사 (F01: ambiguous=True)
    #        "그거는 어떻게 해?"처럼 대상이 생략된 질문은 검색을 돌리기 전에 Rewrite가 먼저 필요합니다.
    if case.get("ambiguous"):
        return STAGE_REWRITE

    # 2단계) 검색 조건 · 접근 권한 검사 (F06: authorized=False)
    #        권한이 없는 문서는 검색이나 점수화 대상이 되어서는 안 됩니다.
    if not case.get("authorized", True):
        return STAGE_AUTH

    # 3단계) 검색 조건 · 최신 공개 버전 및 준비 상태 검사 (F07: current=False or ready=False)
    #        과거 규정(v1)이나 미완료 청크가 섞이지 않도록 Metadata 필터를 먼저 확인합니다.
    if not case.get("current", True) or not case.get("ready", True):
        return STAGE_VERSION

    # 4단계) 1차 검색 · 후보 포함 여부 검사 (F02: gold_in_candidates=False)
    #        필터가 정상인데도 1차 검색 후보(Top-k) 안에 정답 문서가 전혀 없는 상태입니다.
    #        ※ 중요: Reranker는 이미 뽑힌 후보의 순서만 바꾸므로, 이 문제를 절대 해결할 수 없습니다!
    if not case.get("gold_in_candidates", False):
        return STAGE_RETRIEVAL

    # 5단계) 2차 정렬 · Context 포함 여부 검사 (F03: gold_in_candidates=True, gold_in_context=False)
    #        후보 목록에는 정답이 들어왔지만 순위가 뒤로 밀려 Context Top-N에서 잘린 상태입니다.
    #        → 바로 이 지점이 Cross-Encoder Reranking이 효과를 발휘하는 위치입니다!
    if not case.get("gold_in_context", False):
        return STAGE_RERANK

    # 6단계) 생성 후 · 출처·형식 검증 검사 (F04: gold_in_context=True, valid_source=False)
    #        Context에 정답 근거가 잘 들어갔음에도 모델이 허용되지 않은 출처 ID 등을 낸 검증 실패 상태입니다.
    if case.get("valid_source") is False:
        return STAGE_VALIDATION

    # 7단계) 모든 단계 정상 통과 (F05)
    return STAGE_HEALTHY
    # END D27-01-B01


def recommend_action(stage: str) -> str:
    """문제 단계에 맞는 개선 방법을 반환합니다. Reranker는 누락된 후보를 새로 찾지 않습니다."""
    # BEGIN D27-01-B02
    # [흐름 이해: 진단된 단계(stage)에 맞는 정확한 처방 매핑]
    # - 알 수 없는 단계 문자열이나 빈 값이 들어오면 조용히 넘어가지 않고 ValueError로 차단합니다.
    # - 특히 STAGE_RETRIEVAL(후보 누락)일 때는 "Reranker를 쓰면 된다"가 아니라
    #   검색 범위·Query Expansion·Multi-query·인덱싱을 점검해야 한다는 처방을 반환합니다.
    if not isinstance(stage, str) or stage not in ACTION_BY_STAGE:
        raise ValueError(f"지원하지 않는 진단 단계입니다: {stage!r}")

    return ACTION_BY_STAGE[stage]
    # END D27-01-B02


def main():
    # 1) 실행 옵션 파싱 (--offline: 교육용 고정 진단 사례 실행)
    parser = argparse.ArgumentParser(description="Day27 실습 01 · 01_failure_diagnosis")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    # 2) STAGE_RUNNERS[1]에 우리가 작성한 [diagnose_stage, recommend_action] 함수를 주입해 실행
    report = STAGE_RUNNERS[1](args.offline, [diagnose_stage, recommend_action])

    # 3) 실행 모드에 맞는 파일명(day27_01_fixture.json 또는 day27_01_live.json)으로 outputs/ 저장
    path = save_report(
        HERE,
        "day27_01_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 01 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()