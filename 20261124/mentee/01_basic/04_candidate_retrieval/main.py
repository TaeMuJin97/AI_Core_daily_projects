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
from langchain_core.documents import Document
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report

# -----------------------------------------------------------------------------
# 2. 검색 계약 상수 (README.md 및 Day26/27 SQL 검색 상한과 일치)
# -----------------------------------------------------------------------------
MAX_CANDIDATE_K = 20
MAX_CONTEXT_K = 3
REQUIRED_META_KEYS = (
    "chunk_id",
    "citation_id",
    "doc_id",
    "source_version",
    "source_locator",
    "category",
)


def make_candidate_request(case: dict) -> dict:
    """candidate_k와 context_k는 다른 제한값입니다."""
    # BEGIN D27-04-B01
    # [흐름 이해: Retriever에 넘길 검색 요청 계약(payload) 구성 및 검증]
    # 1) 검색용 질문은 Rewrite 결과가 있으면 search_query를, 없으면 원본 question을 사용합니다.
    # 2) candidate_k(1차 검색 후보 수, 최대 20)와 context_k(최종 Context 포함 수, 최대 3)를
    #    서로 다른 제한값으로 분리해 설정합니다.
    # 3) 후보 수가 최종 Context 수보다 적으면(candidate_k < context_k) 논리 모순이므로 차단합니다.
    if not isinstance(case, dict):
        raise ValueError("case는 dict 형식이어야 합니다.")

    query = str(case.get("search_query") or case.get("question") or "").strip()
    if not query:
        raise ValueError("검색 질의(query)는 비어 있을 수 없습니다.")

    category = str(case.get("category") or "").strip()
    if not category:
        raise ValueError("category 필터는 비어 있을 수 없습니다.")

    candidate_k = int(case.get("candidate_k", 5))
    context_k = int(case.get("context_k", 2))

    if not (1 <= candidate_k <= MAX_CANDIDATE_K):
        raise ValueError(f"candidate_k는 1..{MAX_CANDIDATE_K} 범위여야 합니다: {candidate_k}")
    if not (1 <= context_k <= MAX_CONTEXT_K):
        raise ValueError(f"context_k는 1..{MAX_CONTEXT_K} 범위여야 합니다: {context_k}")
    if candidate_k < context_k:
        raise ValueError(f"candidate_k({candidate_k})는 context_k({context_k}) 이상이어야 합니다.")

    return {
        "query": query,
        "category": category,
        "candidate_k": candidate_k,
        "context_k": context_k,
    }
    # END D27-04-B01


def fetch_documents(retriever, payload: dict) -> list[Document]:
    """Day26에서 배운 Runnable.invoke로 후보 Document를 받아옵니다."""
    # BEGIN D27-04-B02
    # [흐름 이해: Runnable Retriever 실행 후 Document 계약·메타데이터·필터 일치 검증]
    # 1) retriever.invoke(payload)를 호출해 E5 + pgvector(또는 offline fixture) 후보를 가져옵니다.
    # 2) 반환된 후보 개수가 요청한 candidate_k를 초과하지 않는지 확인합니다.
    # 3) 모든 항목이 LangChain Document이고, 6개 필수 출처 메타데이터와 요청 category가
    #    유실·변조되지 않고 보존되었는지 검사합니다.
    if not isinstance(payload, dict):
        raise ValueError("payload는 dict 형식이어야 합니다.")

    candidate_k = int(payload.get("candidate_k", 0))
    if not (1 <= candidate_k <= MAX_CANDIDATE_K):
        raise ValueError(f"유효하지 않은 candidate_k입니다: {candidate_k}")

    docs = retriever.invoke(payload)

    if not isinstance(docs, list):
        raise TypeError("Retriever는 Document 리스트를 반환해야 합니다.")
    if len(docs) > candidate_k:
        raise ValueError(f"반환 후보 수({len(docs)})가 candidate_k({candidate_k})를 초과했습니다.")

    expected_category = payload.get("category")
    for doc in docs:
        if not isinstance(doc, Document):
            raise TypeError("반환 목록에 Document가 아닌 객체가 포함되어 있습니다.")
        missing = [k for k in REQUIRED_META_KEYS if k not in doc.metadata]
        if missing:
            raise KeyError(f"Document.metadata에 필수 필드가 누락되었습니다: {missing}")
        if expected_category and doc.metadata.get("category") != expected_category:
            raise ValueError(
                f"Category 필터 불일치: 요청={expected_category}, 문서={doc.metadata.get('category')}"
            )

    return docs
    # END D27-04-B02


def main():
    parser = argparse.ArgumentParser(description="Day27 실습 04 · 04_candidate_retrieval")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    report = STAGE_RUNNERS[4](args.offline, [make_candidate_request, fetch_documents])
    path = save_report(
        HERE,
        "day27_04_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 04 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()