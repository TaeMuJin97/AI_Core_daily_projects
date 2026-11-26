"""04 · 기존 RAG를 rag_search Tool로 · 응용 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def prepare_search(query: str, category: str = 'ALL') -> dict:
    """실제 6개 카테고리만 허용하고 query/category를 반환."""
    # TODO D29-04-I-01: 실제 6개 카테고리만 허용하고 query/category를 반환.
    # 힌트: 실제 query/category 검증 후 coursekit.rag의 live 연결을 호출하세요.
    raise NotImplementedError('D29-04-I-01: 직접 구현하세요')

def invoke_rag(request: dict) -> dict:
    """실제 기존 DB의 pgvector/CUDA RAG를 호출합니다. 가짜 검색 결과 금지."""
    # TODO D29-04-I-02: 실제 기존 DB의 pgvector/CUDA RAG를 호출합니다. 가짜 검색 결과 금지.
    # 힌트: 실제 query/category 검증 후 coursekit.rag의 live 연결을 호출하세요.
    raise NotImplementedError('D29-04-I-02: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_04 import format_evidence
