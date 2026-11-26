"""용도별 추가 검증: Intermediate · Day29."""

def needs_two_sources(plan: dict) -> bool:
    """문서 검색 Tool과 DB Tool이 모두 필요한 계획인지 확인."""
    # 해설 D29-01-I-03: 업무 질문에서 문서 근거 조회와 구조화 상태 조회를 구분합니다.
    # 검수 기준: 규칙 기반 라우팅을 LLM Agent의 자율 선택과 혼동하지 않습니다.
    return set(plan['tools'])=={'rag_search','lookup_status'}

