"""Day28 실습 02 · 01_basic · 실행 진입점.
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


def select_gold(question_id: str, gold: dict) -> list[str]:
    """gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요."""
    # TODO D28-02-B01
    # [흐름 이해: 사전에 사람이 고정한 Gold dict에서 해당 질문의 정답 청크 ID 추출]
    # 1) question_id와 gold dict의 유효성을 검사합니다. (등록되지 않은 질문 ID면 KeyError)
    # 2) 무정답(No-answer) 질문은 [] (빈 리스트)를 그대로 반환합니다.
    # 3) 혹시 원본 목록에 중복 ID가 있더라도 원래 순서를 유지하면서 중복을 제거(dict.fromkeys)합니다.
    if not isinstance(question_id, str) or not question_id.strip():
        raise ValueError("question_id는 비어 있지 않은 문자열이어야 합니다.")
    if not isinstance(gold, dict):
        raise ValueError("gold는 dict 형식이어야 합니다.")
    if question_id not in gold:
        raise KeyError(f"gold 데이터에 존재하지 않는 question_id입니다: {question_id}")

    raw_ids = gold[question_id]
    if raw_ids is None:
        return []
    if not isinstance(raw_ids, (list, tuple, set)):
        raise TypeError("gold[question_id]는 청크 ID 목록(list/tuple/set)이어야 합니다.")

    # 원래 순서를 보존하면서 중복 제거 + 문자열 검사
    unique_ids: list[str] = []
    seen: set[str] = set()
    for cid in raw_ids:
        if not isinstance(cid, str) or not cid.strip():
            raise ValueError(f"유효하지 않은 chunk_id가 포함되어 있습니다: {cid!r}")
        if cid not in seen:
            seen.add(cid)
            unique_ids.append(cid)

    return unique_ids


def validate_gold_ids(ids: list[str], corpus: dict) -> bool:
    """ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요."""
    # TODO D28-02-B02
    # [흐름 이해: Gold 레이블의 정합성 2중 검사]
    # 1) 중복 검사: len(ids) == len(set(ids))
    # 2) 존재 검사: set(ids).issubset(corpus.keys())
    # ※ No-answer 질문의 빈 리스트([])는 중복도 없고 공집합은 모든 집합의 부분집합이므로 True입니다.
    if not isinstance(ids, list) or not isinstance(corpus, dict):
        return False

    if not all(isinstance(cid, str) and cid.strip() for cid in ids):
        return False

    id_set = set(ids)
    has_no_duplicates = len(ids) == len(id_set)
    all_exist_in_corpus = id_set.issubset(corpus.keys())
    return has_no_duplicates and all_exist_in_corpus


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
        "select_gold": select_gold,
        "validate_gold_ids": validate_gold_ids,
    }
    try:
        result = execute(2, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        failure = {
            "status": "execution_failed",
            "exercise": 2,
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
    print("Day28 실습 2 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()