"""04 · 기존 RAG를 rag_search Tool로 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from coursekit.contracts import search_request


def prepare_search(query: str, category: str = "ALL") -> dict:
    """실제 6개 카테고리만 허용하고 query/category를 반환."""
    # TODO D29-04-B-01
    # [흐름 이해: RAG Tool 실행 전 query·category 입력 계약 검증]
    # 1) coursekit.contracts.search_request()를 사용해:
    #    - query가 1~500자의 비어 있지 않은 문자열인지 검사하고 앞뒤 공백을 정리합니다.
    #    - category를 대문자/공백 정리 후 'ALL' 또는 실제 DB 6종 카테고리
    #      (EXPERIMENT, DAILY_WORK, RESEARCH_PLAN, DATA_PROCESSING, PROMPT, MEETING)만 허용합니다.
    # 2) 검증이 끝난 query와 category를 dict로 반환해 다음 invoke_rag()로 넘깁니다.
    if not isinstance(category, str):
        raise ValueError("category는 문자열이어야 합니다.")

    clean_query, clean_category = search_request(query, category)
    return {
        "query": clean_query,
        "category": clean_category,
    }


def invoke_rag(request: dict) -> dict:
    """실제 기존 DB의 pgvector/CUDA RAG를 호출합니다. 가짜 검색 결과 금지."""
    # TODO D29-04-B-02
    # [흐름 이해: 검증된 요청으로 기존 report_agent_lab CUDA RAG 파이프라인 실행]
    # 1) request가 dict인지 확인하고, 직접 호출된 경우에도 안전하도록
    #    prepare_search()로 query/category 계약을 다시 검증합니다.
    # 2) coursekit.rag.rag_answer()를 호출해 실제 경로를 실행합니다:
    #    CUDA E5(query:) → PostgreSQL pgvector(fresh 벡터 필터) →
    #    CUDA Cross-Encoder(bge-reranker-v2-m3) → OpenAI LLM → 출처 계약 검증.
    # 3) --check 실행 시 무거운 GPU/LLM 모듈 로딩을 피하기 위해 함수 내부에서 import합니다.
    if not isinstance(request, dict):
        raise TypeError("request는 query/category를 담은 dict여야 합니다.")

    validated = prepare_search(
        request.get("query"),
        request.get("category", "ALL"),
    )

    from coursekit.rag import rag_answer

    return rag_answer(
        query=validated["query"],
        category=validated["category"],
    )