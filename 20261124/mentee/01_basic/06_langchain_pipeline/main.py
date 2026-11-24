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
from coursekit.pipeline import create_rag_pipeline  # LCEL 7단계 파이프라인 조립기


def prepare_pipeline_request(case: dict) -> dict:
    """원 질문과 History를 함께 보존하고 검색용 질문은 Chain 내부에서 만듭니다."""
    # BEGIN D27-06-B01
    # [흐름 이해: 파이프라인 입력(RagRequest) 구성]
    # 1) RagRequest 스키마는 질문 필드명으로 'query'를 사용합니다.
    #    따라서 case['question']을 'query'에 담아 원 질문을 그대로 전달합니다.
    # 2) 대화 맥락(history)을 함께 보존하고, 검색용 질문(search_query)은 미리 지정하지 않아
    #    Chain 내부의 rewrite Stage가 생성하도록 맡깁니다(use_rewrite=True).
    # 3) 1차 검색 후보 수(candidate_k=5)와 최종 Context 수(context_k=2), Rerank 활성화를 설정합니다.
    if not isinstance(case, dict):
        raise ValueError("case는 dict 형식이어야 합니다.")

    question = str(case.get("question") or "").strip()
    if not question:
        raise ValueError("case['question']은 비어 있을 수 없습니다.")

    category = str(case.get("category") or "").strip()
    if not category:
        raise ValueError("case['category']는 비어 있을 수 없습니다.")

    return {
        "query": question,                          # RagRequest 원 질문 필드 (trace['original_question']으로 보존)
        "history": list(case.get("history") or []), # 대화 기록 보존 → 내부 rewrite Stage에서 참조
        "category": category,
        "candidate_k": int(case.get("candidate_k", 5)),
        "context_k": int(case.get("context_k", 2)),
        "use_rewrite": True,
        "use_multiquery": False,
        "use_rerank": True,
    }
    # END D27-06-B01


def wire_langchain_pipeline(dependencies: tuple, offline: bool):
    """LCEL는 Runnable을 준비할 뿐이고 .invoke()가 실행 시작점입니다."""
    # BEGIN D27-06-B02
    # [흐름 이해: 주입받은 4개 의존성을 LCEL Runnable 체인으로 조립]
    # - dependencies는 create_dependencies(offline)가 반환한 (rewrite, search, rerank, generate) 튜플입니다.
    # - create_rag_pipeline() 내부에서는
    #     start | rewrite | multiquery | retrieval | rerank | context | generation
    #   순서로 RunnableLambda들을 파이프(|)로 연결합니다.
    # - 이 함수는 실행 계획(Runnable)만 조립해 반환하며, 실제 DB/GPU/LLM 호출은
    #   workshops.py의 run_06()에서 chain.invoke(req)를 부르는 순간 시작됩니다.
    if not isinstance(dependencies, (tuple, list)) or len(dependencies) != 4:
        raise ValueError("dependencies는 (rewrite, search, rerank, generate) 4개 요소여야 합니다.")

    rewrite_fn, search_fn, rank_fn, generation_fn = dependencies
    return create_rag_pipeline(
        rewrite_fn,
        search_fn,
        rank_fn,
        generation_fn,
        offline=offline,
    )
    # END D27-06-B02


def main():
    parser = argparse.ArgumentParser(description="Day27 실습 06 · 06_langchain_pipeline")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    report = STAGE_RUNNERS[6](args.offline, [prepare_pipeline_request, wire_langchain_pipeline])
    path = save_report(
        HERE,
        "day27_06_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 06 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()