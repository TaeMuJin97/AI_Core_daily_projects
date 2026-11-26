"""경계값·오류/권한 정책: Advanced · Day29."""

def needs_two_sources(plan: dict) -> bool:
    """문서 검색 Tool과 DB Tool이 모두 필요한 계획인지 확인."""
    # 해설 D29-01-A-03: 업무 질문에서 문서 근거 조회와 구조화 상태 조회를 구분합니다.
    # 검수 기준: 규칙 기반 라우팅을 LLM Agent의 자율 선택과 혼동하지 않습니다.
    return set(plan['tools'])=={'rag_search','lookup_status'}

def validate_plan(plan: dict) -> dict:
    """등록되지 않은 Tool·중복 Tool·상태 누락을 진단."""
    # 해설 D29-01-A-04: 업무 질문에서 문서 근거 조회와 구조화 상태 조회를 구분합니다.
    # 검수 기준: 규칙 기반 라우팅을 LLM Agent의 자율 선택과 혼동하지 않습니다.
    allowed={'rag_search','lookup_status'}
    names=plan.get('tools',[])
    if not isinstance(names,list) or not names or len(names)!=len(set(names)) or not set(names)<=allowed:
        raise ValueError('Tool 계획이 등록 목록·중복 정책을 위반합니다.')
    return {'valid':True,'tools':names}

