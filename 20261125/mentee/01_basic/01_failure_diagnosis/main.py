"""Day28 실습 01 · 01_basic · 실행 진입점.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""
from pathlib import Path
import argparse
import sys

ROLE_ROOT = Path(__file__).resolve().parents[2]
if str(ROLE_ROOT) not in sys.path:
    sys.path.insert(0, str(ROLE_ROOT))

from coursekit.eval_workshops import execute
from coursekit.eval_report import write_json


def classify_case(case: dict) -> str:
    """case의 system_error·candidate_has_gold·context_has_gold·answer_grounded를 차례로 확인하고 stage 문자열을 반환하세요. 시스템 장애와 검색 실패를 구분하세요."""
    # TODO D28-01-B01
    # [흐름 이해: System → Candidate(Retrieval) → Context(Rerank/Builder) → Generation 순차 진단]
    # 1) 시스템 장애(DB·GPU·API 오류)가 발생했다면 검색/생성 품질 문제와 반드시 분리합니다.
    # 2) 1차 검색 후보에 Gold가 없으면(False) Reranker나 LLM으로 복구할 수 없는 Retrieval 실패입니다.
    # 3) 후보에는 Gold가 있었는데 실제 Context에 못 들어갔다면(False) Reranker·Context 선택 실패입니다.
    # 4) Context에 Gold가 들어갔는데도 답변이 근거를 지키지 못했다면(False) Generation 실패입니다.
    # ※ No-answer 사례 등에서 값이 None일 수 있으므로 `not val` 대신 `is False`로 안전하게 검사합니다.
    if not isinstance(case, dict):
        raise ValueError("case는 dict 형식이어야 합니다.")

    if bool(case.get("system_error")):
        return "system_error"
    if case.get("candidate_has_gold") is False:
        return "retrieval"
    if case.get("context_has_gold") is False:
        return "rerank_or_context"
    if case.get("answer_grounded") is False:
        return "generation"
    return "ok"


def describe_evidence(case: dict, stage: str) -> str:
    """분류된 stage를 설명할 수 있는 구체적인 한 줄의 근거를 반환하세요. 빈 문자열은 안 됩니다."""
    # TODO D28-01-B02
    # [흐름 이해: 분류 결과(stage)에 대응하는 1줄 근거 작성 — 후보 누락과 Context 누락을 명확히 구분]
    if not isinstance(case, dict):
        raise ValueError("case는 dict 형식이어야 합니다.")
    if not isinstance(stage, str) or not stage.strip():
        raise ValueError("stage는 비어 있을 수 없습니다.")

    qid = case.get("question_id") or case.get("case_id") or case.get("id") or "사례"

    if stage == "system_error":
        return (
            f"[{qid}] 시스템 장애(system_error=True)가 발생해 정상 검색/생성이 중단되었으므로 "
            "검색·생성 품질 실패와 분리해 인프라·API·예외 처리를 점검해야 합니다."
        )
    if stage == "retrieval":
        return (
            f"[{qid}] 1차 검색 후보에 정답 문서가 포함되지 않았으므로(candidate_has_gold=False) "
            "Reranker가 아닌 Query Rewrite·필터·임베딩·인덱스(Retriever)를 점검해야 합니다."
        )
    if stage == "rerank_or_context":
        return (
            f"[{qid}] 1차 검색 후보에는 정답 문서가 있었으나(candidate_has_gold=True) "
            "최종 Context에서 탈락했으므로(context_has_gold=False) Reranker 순위와 Context 선택·길이 예산을 점검해야 합니다."
        )
    if stage == "generation":
        return (
            f"[{qid}] 정답 문서가 실제 Context에 포함되었으나(context_has_gold=True) "
            "생성 답변이 근거와 일치하지 않으므로(answer_grounded=False) Prompt와 Generator를 점검해야 합니다."
        )
    return (
        f"[{qid}] 시스템 장애 없이 검색 후보·Context에 근거가 포함되었고 답변이 근거를 충족하므로 "
        "출처 ID 및 원문 정합성을 유지합니다."
    )


def main():
    parser = argparse.ArgumentParser(description="Day28 RAG Evaluation 실습")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="고정 학습 데이터만 실행(기본값)")
    mode.add_argument("--live", action="store_true", help="실제 CUDA GPU/DB/LLM 연결. 06~08만 지원하며 API 비용 발생 가능")
    args = parser.parse_args()
    hooks = {
        "classify_case": classify_case,
        "describe_evidence": describe_evidence,
    }
    try:
        result = execute(1, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        failure = {
            "status": "execution_failed",
            "exercise": 1,
            "stage": getattr(exc, "stage", "evaluation"),
            "error_type": type(exc).__name__,
            "mode": "live" if args.live else "offline_fixture",
        }
        write_json(Path(__file__).resolve().parent / "outputs" / "failure.json", failure)
        raise
    output = Path(__file__).resolve().parent / "outputs" / "result.json"
    write_json(output, result)
    if isinstance(result.get("markdown_report"), str):
        (output.parent / "report.md").write_text(result["markdown_report"], encoding="utf-8")
    print("Day28 실습 1 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()