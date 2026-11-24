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
from coursekit.rewrite import rewrite_query  # offline 고정 예시 / live ChatPromptTemplate|ChatModel 실행기

# -----------------------------------------------------------------------------
# 2. 상태 상수 정의 (coursekit.rewrite.RewriteResult 계약과 일치)
# -----------------------------------------------------------------------------
STATUS_READY = "ready"
STATUS_CLARIFICATION_REQUIRED = "clarification_required"


def apply_rewrite(question: str, history: list[dict], offline: bool):
    """offline이면 고정 예시, 기본 실행이면 실제 ChatPromptTemplate → Chat Model을 호출합니다."""
    # BEGIN D27-02-B01
    # [흐름 이해: 키워드 인자(offline=offline)로 Rewrite 실행기 호출]
    # - rewrite_query(original_question, history, *, offline=False)는
    #   offline이 키워드 전용 인자이므로 반드시 offline=offline으로 전달합니다.
    # - 반환값은 RewriteResult(status, search_query, reason) 객체입니다.
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question은 비어 있지 않은 문자열이어야 합니다.")

    safe_history = list(history) if history else []
    return rewrite_query(question, safe_history, offline=offline)
    # END D27-02-B01


def record_rewrite(original: str, result) -> dict:
    """원래 질문을 검색 질문으로 덮어쓰지 않습니다."""
    # BEGIN D27-02-B02
    # [흐름 이해: 원래 질문(original) 보존 & RewriteResult(status, search_query, reason) 기록]
    # - original_question은 사용자가 입력한 원문 그대로 절대 덮어쓰지 않고 보관합니다.
    # - status가 "clarification_required"이거나 search_query가 비어 있으면
    #   대상을 추측하지 않고 확인 요청 상태로 기록합니다.
    if not isinstance(original, str) or not original.strip():
        raise ValueError("original 질문은 비어 있지 않은 문자열이어야 합니다.")

    if isinstance(result, dict):
        status = result.get("status", STATUS_CLARIFICATION_REQUIRED)
        search_query = str(result.get("search_query", "") or "").strip()
        reason = str(result.get("reason", "") or "")
    else:
        status = getattr(result, "status", STATUS_CLARIFICATION_REQUIRED)
        search_query = str(getattr(result, "search_query", "") or "").strip()
        reason = str(getattr(result, "reason", "") or "")

    if status != STATUS_READY or not search_query:
        return {
            "status": STATUS_CLARIFICATION_REQUIRED,
            "original_question": original,   # 사용자가 보낸 원문 질문 그대로 보존
            "search_query": "",              # 대상을 확정할 수 없으므로 검색 질의 비움
            "reason": reason or "대화에서 대상을 확인할 수 없습니다.",
        }

    return {
        "status": STATUS_READY,
        "original_question": original,       # 최종 답변 생성(Generator)용 원문 질문 보존
        "search_query": search_query,        # Retriever · Reranker 전용 독립 질문
        "reason": reason,
    }
    # END D27-02-B02


def main():
    parser = argparse.ArgumentParser(description="Day27 실습 02 · 02_query_rewrite")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    report = STAGE_RUNNERS[2](args.offline, [apply_rewrite, record_rewrite])
    path = save_report(
        HERE,
        "day27_02_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 02 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()