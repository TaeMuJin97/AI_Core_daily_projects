"""Day28 실습 07 · 01_basic · 실행 진입점.
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


def score_delta(before: float | None, after: float | None) -> float | None:
    """같은 질문의 Before/After 점수 변화량을 계산하세요. No-answer(None)는 수치 차이를 만들지 않습니다."""
    # TODO D28-07-B01
    # [흐름 이해: 동일 질문·동일 Dataset 버전·동일 실행 모드에서의 Delta = after - before]
    # 1) No-answer 질문 등으로 before 또는 after가 None이면 수치 차이를 만들지 않고 None을 반환합니다.
    # 2) bool은 int의 하위 타입이므로 숫자로 잘못 계산되지 않도록 제외합니다.
    # 3) 부동소수점 오차(예: 0.30000000000000004)를 줄이기 위해 소수점 4자리에서 반올림합니다.
    if before is None or after is None:
        return None
    if (
        not isinstance(before, (int, float))
        or isinstance(before, bool)
        or not isinstance(after, (int, float))
        or isinstance(after, bool)
    ):
        raise TypeError("before와 after는 숫자(int/float) 또는 None이어야 합니다.")

    return round(float(after) - float(before), 4)


def find_problem_stage(run: dict, gold: list[str]) -> str:
    """검색 후보 누락·Reranking 누락·Context 누락·생성 실패 중 어디인지 반환하세요."""
    # TODO D28-07-B02
    # [흐름 이해: 앞 단계부터 순차적으로 실패 지점 특정]
    # 1) 시스템 오류(error / system_error) → "system_error"
    # 2) Gold가 빈 무정답(No-answer) 질문:
    #    - 정상 거절(insufficient_context)이면 "no_answer_ok"
    #    - 근거가 없는데 답변을 생성했으면 "generation"
    # 3) 1차 검색 후보(candidate_ids)에 Gold가 없으면 → "retrieval" (Reranker로 복구 불가)
    # 4) 후보엔 있었으나 최종 Context(included_ids)에 Gold가 없다면:
    #    - 재정렬 결과(ranked_ids) 상위 슬롯(context_k 범위)에 못 들었으면 → "reranking"
    #    - 상위 순위에는 들었으나 글자 예산 등 Context 구성에서 탈락했으면 → "context"
    # 5) Context에 Gold가 들어갔는데도 answered가 아니거나 근거 불일치면 → "generation"
    # 6) 모든 단계를 정상 통과하면 → "ok"
    if not isinstance(run, dict):
        raise TypeError("run은 실행 결과를 담은 dict여야 합니다.")
    if not isinstance(gold, (list, set, tuple)):
        raise TypeError("gold는 청크 ID 목록(list/set/tuple)이어야 합니다.")

    status = run.get("status")
    if run.get("system_error") or run.get("error") or status in {"error", "failed", "system_error"}:
        return "system_error"

    gold_set = set(gold)
    if not gold_set:
        if status == "insufficient_context":
            return "no_answer_ok"
        return "generation"

    candidate_ids = list(
        run["candidate_ids"] if "candidate_ids" in run else run.get("ranked_ids", [])
    )
    ranked_ids = list(run.get("ranked_ids", []))
    included_ids = list(run.get("included_ids", []))

    # 1차 후보(Candidate) 자체에 정답이 없는 경우 → Retrieval 실패
    if not (set(candidate_ids) & gold_set):
        return "retrieval"

    # 최종 Context에 정답이 포함되지 않은 경우 → Reranking 순위 문제 vs Context 예산 문제 구분
    if not (set(included_ids) & gold_set):
        if not (set(ranked_ids) & gold_set):
            return "reranking"
        # Context 슬롯 수(기본 Top-2) 안에 정답이 들지 못했으면 Reranking 순위 문제
        top_slot = len(included_ids) if included_ids else 2
        if not (set(ranked_ids[:top_slot]) & gold_set):
            return "reranking"
        return "context"

    # Context에 정답이 포함되었으나 답변 생성/근거 검증이 실패한 경우
    if run.get("answer_grounded") is False or (status is not None and status != "answered"):
        return "generation"

    return "ok"


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
        "score_delta": score_delta,
        "find_problem_stage": find_problem_stage,
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result = execute(7, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure = {
            "status": "execution_failed",
            "exercise": 7,
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
    print("Day28 실습 7 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()