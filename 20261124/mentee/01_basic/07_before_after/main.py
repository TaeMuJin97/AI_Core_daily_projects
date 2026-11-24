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
# 2. 비교 기준 상수 (README.md 및 test_exercise.py의 Top-2 계약과 일치)
# -----------------------------------------------------------------------------
DEFAULT_TOP_K = 2


def _best_rank(ranked_ids: list[str], gold_set: set[str]) -> int | None:
    """관련 문서(gold) 중 가장 높은 순위(1부터 시작)를 반환합니다. 없으면 None."""
    for idx, chunk_id in enumerate(ranked_ids, start=1):
        if chunk_id in gold_set:
            return idx
    return None


def compare_rankings(
    before: list[str],
    after: list[str],
    gold: list[str] | set[str],
    k: int = DEFAULT_TOP_K,
) -> dict:
    """고정한 관련 문서 ID를 Top-2에 포함했는지 확인합니다."""
    # BEGIN D27-07-B01
    # [흐름 이해: 동일 후보에 대한 Before(1차 검색) vs After(Rerank) 비교표 만들기]
    # 1) 입력 목록과 k(기본값 2)를 검증합니다.
    # 2) 사전에 고정한 gold ID를 기준으로:
    #    - before[:k] / after[:k]에 관련 문서가 하나라도 포함되었는지(Hit@2) 확인합니다.
    #    - 1차 후보(before) 자체에 정답이 있었는지(gold_in_candidates) 함께 기록해
    #      후보 누락(Recall Ceiling)과 순위 문제를 구분합니다.
    #    - 가장 높은 관련 문서 순위(1-based) 변화와 전체 순서 변경 여부도 남깁니다.
    if not isinstance(before, list) or not isinstance(after, list):
        raise ValueError("before와 after는 chunk_id 리스트여야 합니다.")
    if not isinstance(k, int) or k < 1:
        raise ValueError("k는 1 이상의 정수여야 합니다.")

    gold_list = list(gold or [])
    gold_set = set(gold_list)

    before_top_k = before[:k]
    after_top_k = after[:k]

    before_hit = any(cid in gold_set for cid in before_top_k)
    after_hit = any(cid in gold_set for cid in after_top_k)
    gold_in_candidates = any(cid in gold_set for cid in before)

    return {
        "k": k,  # test_exercise.py 필수 계약: comparison['k'] == 2
        "gold_ids": gold_list,
        "before_ids": list(before),
        "after_ids": list(after),
        "before_top_k": before_top_k,
        "after_top_k": after_top_k,
        "gold_in_candidates": gold_in_candidates,
        "before_in_top_k": before_hit,
        "after_in_top_k": after_hit,
        "before_best_rank": _best_rank(before, gold_set),
        "after_best_rank": _best_rank(after, gold_set),
        "order_changed": before != after,
    }
    # END D27-07-B01


def interpret_change(report: dict) -> str:
    """순위가 바뀌어도 반드시 개선됐다는 결론을 내리지 않습니다."""
    # BEGIN D27-07-B02
    # [흐름 이해: 비교 결과(report)에 대한 신중한 해석]
    # - 단순 순위 변경만으로 "항상 개선됐다"고 단정하지 않고,
    #   ① 후보 존재 여부(Recall Ceiling), ② Top-k 진입/이탈(회귀) 여부,
    #   ③ 지연 시간(Latency) 증가와 실제 답변 Grounding 별도 확인 필요성을 함께 명시합니다.
    if not isinstance(report, dict):
        raise ValueError("report는 compare_rankings()가 반환한 dict여야 합니다.")

    k = report.get("k", DEFAULT_TOP_K)
    gold_ids = report.get("gold_ids", [])
    gold_in_candidates = bool(report.get("gold_in_candidates", False))
    before_hit = bool(report.get("before_in_top_k", False))
    after_hit = bool(report.get("after_in_top_k", False))
    before_rank = report.get("before_best_rank")
    after_rank = report.get("after_best_rank")
    order_changed = bool(report.get("order_changed", False))

    if not gold_ids:
        return (
            "사전 정의된 관련 문서(gold)가 없어 Top-k 포함 여부를 판정할 수 없습니다. "
            "답변 불가 질문인지 또는 평가 기준을 먼저 확정해야 합니다."
        )

    if not gold_in_candidates:
        return (
            "1차 검색 후보에 관련 문서가 전혀 없습니다(Recall Ceiling). "
            "순위가 바뀌었더라도 Reranker만으로 해결할 수 없으므로 검색 범위·필터·질의 확장을 점검해야 합니다."
        )

    if not before_hit and after_hit:
        return (
            f"관련 문서가 Top-{k} 밖({before_rank}위)에서 Top-{k} 안({after_rank}위)으로 진입했습니다. "
            "단, 단일 질문의 순위 개선만으로 전체 품질이나 답변 Grounding이 보장되지는 않으므로 "
            "원문 대조·지연 시간(Latency)·다수 질문 평가(Day28)를 함께 확인해야 합니다."
        )

    if before_hit and not after_hit:
        return (
            f"회귀(Regression) 발생: 기존 Top-{k} 안({before_rank}위)에 있던 관련 문서가 "
            f"재정렬 후 Top-{k} 밖({after_rank}위)으로 밀려났습니다. "
            "Reranker 모델 적합성과 후보 구성을 재검토해야 합니다."
        )

    if before_hit and after_hit:
        change_note = (
            f"순위 변동은 관찰됨({before_rank}위 → {after_rank}위, 전체 순서 변경={order_changed})"
            if order_changed
            else "전체 순위 변화 없음"
        )
        return (
            f"전후 모두 Top-{k}에 관련 문서가 포함되었습니다({change_note}). "
            "순위가 바뀌었더라도 반드시 개선됐다고 단정할 수 없으며, "
            "추가 Rerank 소요 시간(Latency) 대비 효용과 실제 답변 Grounding을 별도로 확인해야 합니다."
        )

    return (
        f"관련 문서가 후보에는 있으나 재정렬 후에도 Top-{k} 안에 들어오지 못했습니다"
        f"({before_rank}위 → {after_rank}위). "
        "순위가 일부 바뀌었더라도 개선으로 단정할 수 없으며 Reranker 모델·context_k·질의를 점검해야 합니다."
    )
    # END D27-07-B02


def main():
    parser = argparse.ArgumentParser(description="Day27 실습 07 · 07_before_after")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    report = STAGE_RUNNERS[7](args.offline, [compare_rankings, interpret_change])
    path = save_report(
        HERE,
        "day27_07_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 07 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()