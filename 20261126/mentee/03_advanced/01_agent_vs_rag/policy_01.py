"""경계값·오류/권한 정책: Advanced · Day29."""

def needs_two_sources(plan: dict) -> bool:
    """문서 검색 Tool과 DB Tool이 모두 필요한 계획인지 확인."""
    # TODO D29-01-A-03: 문서 검색 Tool과 DB Tool이 모두 필요한 계획인지 확인.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    raise NotImplementedError('D29-01-A-03: 직접 구현하세요')

def validate_plan(plan: dict) -> dict:
    """등록되지 않은 Tool·중복 Tool·상태 누락을 진단."""
    # TODO D29-01-A-04: 등록되지 않은 Tool·중복 Tool·상태 누락을 진단.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    raise NotImplementedError('D29-01-A-04: 직접 구현하세요')

