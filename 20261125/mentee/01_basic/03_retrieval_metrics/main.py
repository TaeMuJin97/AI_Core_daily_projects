"""Day28 실습 03 · 01_basic · 실행 진입점.
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


def count_gold_hits(ranked: list[str], gold: list[str], k: int) -> int:
    """Top-k 목록과 Gold의 교집합 크기를 반환하세요. 중복 ID는 한 번만 셉니다."""
    # TODO D28-03-B02
    # [흐름 이해: Top-k 검색 결과에 실제 정답(Gold)이 몇 개 들어왔는지 교집합으로 계산]
    # 1) k는 1 이상의 양의 정수여야 합니다 (bool은 int의 하위 타입이므로 제외).
    # 2) ranked[:k]를 set으로 변환해 동일 chunk_id가 중복 반환되어도 1번만 카운트합니다.
    # 3) set(ranked[:k]) & set(gold)의 크기(int)를 반환합니다.
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"k는 1 이상의 정수여야 합니다: {k!r}")
    if not isinstance(ranked, list) or not isinstance(gold, (list, set, tuple)):
        raise TypeError("ranked는 list, gold는 list/set/tuple 형식이어야 합니다.")

    top_k = set(ranked[:k])
    gold_set = set(gold)
    return len(top_k & gold_set)


def calculate_recall(ranked: list[str], gold: list[str], k: int) -> float | None:
    """Top-k에서 찾은 Gold 개수 / 전체 Gold 개수를 계산하세요. Gold가 빈 질문은 None을 반환하세요."""
    # TODO D28-03-B01
    # [흐름 이해: Recall@k = |Gold ∩ Top-k| / |Gold|]
    # 1) k가 1 미만이면 즉시 ValueError를 발생시킵니다.
    # 2) Gold가 비어 있는 무정답(No-answer) 질문은 분모가 0이므로 0.0이 아니라 None(N/A)을 반환합니다.
    #    (0.0으로 합산하면 전체 Retrieval 평균이 인위적으로 낮아져 왜곡됩니다.)
    # 3) count_gold_hits()로 중복 제거된 일치 개수를 구한 뒤 전체 고유 Gold 개수로 나눕니다.
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError(f"k는 1 이상의 정수여야 합니다: {k!r}")
    if not isinstance(ranked, list) or not isinstance(gold, (list, set, tuple)):
        raise TypeError("ranked는 list, gold는 list/set/tuple 형식이어야 합니다.")

    gold_set = set(gold)
    if not gold_set:
        return None

    hits = count_gold_hits(ranked, list(gold_set), k)
    return hits / len(gold_set)


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
        "calculate_recall": calculate_recall,
        "count_gold_hits": count_gold_hits,
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result = execute(3, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure = {
            "status": "execution_failed",
            "exercise": 3,
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
    print("Day28 실습 3 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()