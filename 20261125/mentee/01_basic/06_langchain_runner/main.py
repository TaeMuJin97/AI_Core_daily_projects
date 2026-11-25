"""Day28 실습 06 · 01_basic · 실행 진입점.
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


def safe_target_input(example: dict) -> dict:
    """question_id·question·category·history만 새 dict로 복사하고 Gold·Reference를 제외하세요."""
    # TODO D28-06-B01
    # [흐름 이해: Gold Leakage 방지를 위한 화이트리스트 기반 입력 정제]
    # 1) example dict에서 gold_chunk_ids, relevance_grades, reference_answer 등은 전부 제외합니다.
    # 2) 실제 서비스(Target)가 알아야 할 4개 필드(question_id, question, category, history)만
    #    새 dict로 복사해 반환합니다. (history는 원본 리스트 변형을 막기 위해 새 list로 복사)
    if not isinstance(example, dict):
        raise TypeError("example은 dict 형식이어야 합니다.")

    for required_key in ("question_id", "question", "category"):
        if required_key not in example:
            raise KeyError(f"example에 필수 키가 누락되었습니다: {required_key}")

    raw_history = example.get("history", [])
    if raw_history is None:
        raw_history = []
    if not isinstance(raw_history, list):
        raise TypeError("history는 list 형식이어야 합니다.")

    return {
        "question_id": example["question_id"],
        "question": example["question"],
        "category": example["category"],
        "history": list(raw_history),
    }


def invoke_target(target, request: dict) -> dict:
    """실제 Runnable.invoke(request)를 호출하고 결과가 dict이며 질문 ID가 같은지 확인하세요."""
    # TODO D28-06-B02
    # [흐름 이해: LangChain Runnable 계약에 맞춘 실행 및 반환 정합성 검증]
    # 1) target이 invoke() 메서드를 가진 Runnable 객체인지 확인합니다.
    # 2) 함수 직접 호출 대신 반드시 target.invoke(request)를 호출합니다.
    #    (Chain 정의 시점이 아니라 invoke() 호출 시점에 실제 DB/GPU/LLM 연산이 실행됩니다.)
    # 3) 반환값이 dict이며, 요청한 question_id와 응답의 question_id가 일치하는지 검증합니다.
    if not hasattr(target, "invoke") or not callable(target.invoke):
        raise TypeError("target은 invoke() 메서드를 제공하는 LangChain Runnable이어야 합니다.")
    if not isinstance(request, dict) or "question_id" not in request:
        raise ValueError("request는 'question_id'를 포함한 dict여야 합니다.")

    result = target.invoke(request)

    if not isinstance(result, dict):
        raise TypeError(f"Runnable.invoke() 결과는 dict여야 합니다: {type(result).__name__}")
    if result.get("question_id") != request["question_id"]:
        raise ValueError(
            f"질문 ID 불일치: 요청={request['question_id']!r}, 응답={result.get('question_id')!r}"
        )

    return result


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
        "safe_target_input": safe_target_input,
        "invoke_target": invoke_target,
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result = execute(6, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure = {
            "status": "execution_failed",
            "exercise": 6,
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
    print("Day28 실습 6 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()