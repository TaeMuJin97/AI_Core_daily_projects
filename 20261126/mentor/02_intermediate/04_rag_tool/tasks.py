"""04 · 기존 RAG를 rag_search Tool로 · 응용 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def prepare_search(query: str, category: str = 'ALL') -> dict:
    """실제 6개 카테고리만 허용하고 query/category를 반환."""
    # 해설 D29-04-I-01: 실제 CUDA E5 query: 인코딩으로 11/20의 overview Vector를 검색합니다.
    # 검수 기준: CUDA CrossEncoder/LLM과 출처 ID 검증의 책임을 분리합니다.
    from coursekit.contracts import search_request
    query,category=search_request(query,category)
    return {'query':query,'category':category}

def invoke_rag(request: dict) -> dict:
    """실제 기존 DB의 pgvector/CUDA RAG를 호출합니다. 가짜 검색 결과 금지."""
    # 해설 D29-04-I-02: 실제 CUDA E5 query: 인코딩으로 11/20의 overview Vector를 검색합니다.
    # 검수 기준: CUDA CrossEncoder/LLM과 출처 ID 검증의 책임을 분리합니다.
    from coursekit.rag import rag_answer
    return rag_answer(request['query'],request['category'])


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_04 import format_evidence
