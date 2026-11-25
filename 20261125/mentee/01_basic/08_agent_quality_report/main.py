"""Day28 실습 08 · 01_basic · 실행 진입점.
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
from coursekit.eval_metrics import evaluate_retrieval, mean_valid

# -----------------------------------------------------------------------------
# 필수 Trace 필드 계약: 누락 시 빈 리스트로 대체하지 않고 즉시 오류로 보고
# -----------------------------------------------------------------------------
REQUIRED_TRACE_FIELDS = {"ranked_ids", "included_ids", "answer", "status"}


def evaluate_one(example: dict, run: dict, gold: list[str], grades: dict) -> dict:
    """질문 ID로 Target 출력과 Gold를 결합해 평가 레코드를 반환하세요."""
    # TODO D28-08-B01
    # [흐름 이해: Target 실행 결과(run)와 사전 고정 Gold를 question_id 기준으로 사후 결합]
    # 1) 필수 Trace 필드(ranked_ids, included_ids, answer, status)가 빠졌으면 ValueError 발생
    # 2) run에 question_id가 있다면 example['question_id']와 일치하는지 검증
    # 3) coursekit.eval_metrics.evaluate_retrieval(..., k=3)로 Recall@3 · RR@3 · nDCG@3 계산
    # 4) 시스템 오류 여부, 출처 ID 유효성, No-answer 여부, Generation 사람 검수 대기 상태를 기록
    if not isinstance(example, dict) or not isinstance(run, dict):
        raise TypeError("example과 run은 dict 형식이어야 합니다.")

    qid = example.get("question_id")
    if not qid:
        raise ValueError("example에 'question_id'가 누락되었습니다.")

    if "question_id" in run and run["question_id"] != qid:
        raise ValueError(
            f"question_id 불일치: dataset={qid!r}, run={run['question_id']!r}"
        )

    missing = REQUIRED_TRACE_FIELDS - set(run.keys())
    if missing:
        raise ValueError(f"필수 Trace 필드 누락({qid}): {sorted(missing)}")

    ranked_ids = run["ranked_ids"]
    included_ids = run["included_ids"]
    if not isinstance(ranked_ids, list) or not isinstance(included_ids, list):
        raise TypeError("ranked_ids와 included_ids는 list 형식이어야 합니다.")

    status = run["status"]
    is_no_answer = len(gold) == 0
    has_error = bool(
        run.get("system_error")
        or run.get("error")
        or status in {"error", "failed", "system_error"}
    )

    # Retrieval 지표 계산 (No-answer 질문은 recall/rr/ndcg가 None으로 반환됨)
    metrics = evaluate_retrieval(ranked_ids, gold, grades, 3)

    # 출처 검증: sources(list[dict])가 있으면 chunk_id가 실제 included_ids 안에 있는지 검사
    included_set = set(included_ids)
    invalid_sources = 0
    for src in run.get("sources", []) or []:
        if isinstance(src, dict):
            src_cid = src.get("chunk_id")
            if src_cid and src_cid not in included_set:
                invalid_sources += 1

    return {
        "question_id": qid,
        "mode": run.get("mode", "unknown"),
        "status": status,
        "is_no_answer": is_no_answer,
        "gold_count": len(gold),
        "ranked_ids": list(ranked_ids),
        "included_ids": list(included_ids),
        "recall_at_3": metrics.get("recall_at_k"),
        "rr_at_3": metrics.get("rr"),
        "ndcg_at_3": metrics.get("ndcg_at_k"),
        "has_error": has_error,
        "invalid_sources": invalid_sources,
        "generation_review": "pending",
    }


def summarize_all(rows: list[dict]) -> dict:
    """개별 질문 결과의 평균(유효 Gold만)과 오류·출처 상태를 집계하세요."""
    # TODO D28-08-B02
    # [흐름 이해: 질문별 레코드를 모아 전체 평균(유효 Gold만) + No-answer/오류/출처 집계]
    # 1) No-answer 질문은 Retrieval 평균에서 제외하고 no_answer_count로 별도 기록
    # 2) mean_valid()로 None을 제외한 유효 질문만의 Recall · MRR · nDCG 평균 계산
    # 3) 오류 건수(error_count)와 허위 출처 건수(invalid_sources) 합산
    # 4) 1차 Quality Gate(precheck_passed) 판정 포함 (단, 실제 Agent 배포 전체 보증은 아님)
    if not isinstance(rows, list):
        raise TypeError("rows는 평가 레코드 dict의 list여야 합니다.")

    total_questions = len(rows)
    no_answer_count = sum(1 for r in rows if r.get("is_no_answer"))
    answerable_count = total_questions - no_answer_count

    recall_mean = mean_valid([r.get("recall_at_3") for r in rows if not r.get("is_no_answer")])
    mrr_mean = mean_valid([r.get("rr_at_3") for r in rows if not r.get("is_no_answer")])
    ndcg_mean = mean_valid([r.get("ndcg_at_3") for r in rows if not r.get("is_no_answer")])

    error_count = sum(1 for r in rows if r.get("has_error"))
    invalid_sources = sum(int(r.get("invalid_sources", 0)) for r in rows)

    checks = {
        "retrieval": recall_mean is not None and recall_mean >= 0.70,
        "ranking": mrr_mean is not None and mrr_mean >= 0.60,
        "citation": invalid_sources == 0,
        "errors": error_count == 0,
    }

    return {
        "total_questions": total_questions,
        "answerable_count": answerable_count,
        "no_answer_count": no_answer_count,
        "recall_mean": round(recall_mean, 4) if recall_mean is not None else None,
        "mrr_mean": round(mrr_mean, 4) if mrr_mean is not None else None,
        "ndcg_mean": round(ndcg_mean, 4) if ndcg_mean is not None else None,
        "error_count": error_count,
        "invalid_sources": invalid_sources,
        "precheck_passed": all(checks.values()),
        "checks": checks,
    }


def main():
    parser = argparse.ArgumentParser(description="Day28 RAG Evaluation 실습")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="고정 학습 데이터만 실행(기본값)")
    mode.add_argument(
        "--live",
        action="store_true",
        help="실제 CUDA GPU/DB/LLM 연결. 06~08만 지원하며 API 비용 발생 가능",
    )
    args = parser.parse_args()
    hooks = {
        "evaluate_one": evaluate_one,
        "summarize_all": summarize_all,
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result = execute(8, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure = {
            "status": "execution_failed",
            "exercise": 8,
            "stage": getattr(exc, "stage", "evaluation"),
            "error_type": type(exc).__name__,
            "mode": "live" if args.live else "offline_fixture",
        }
        write_json(Path(__file__).resolve().parent / "outputs" / "failure.json", failure)
        raise
    output = Path(__file__).resolve().parent / "outputs" / "result.json"
    write_json(output, result)
    # 학생이 코드로 만든 설명 보고서는 별도 Markdown 파일로 저장합니다.
    if isinstance(result.get("markdown_report"), str):
        (output.parent / "report.md").write_text(result["markdown_report"], encoding="utf-8")
    print("Day28 실습 8 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()