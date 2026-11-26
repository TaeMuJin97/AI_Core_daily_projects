"""경계값·오류/권한 정책: Advanced · Day29."""

def schema_fields(tool_obj) -> list[str]:
    """모델에게 노출되는 Tool 입력 필드 이름을 목록으로 반환합니다."""
    # TODO D29-03-A-03: 모델에게 노출되는 Tool 입력 필드 이름을 목록으로 반환합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    raise NotImplementedError('D29-03-A-03: 직접 구현하세요')

def enforce_explicit_schema(tool_obj) -> dict:
    """Tool JSON Schema에 report_id가 required인지 점검합니다."""
    # TODO D29-03-A-04: Tool JSON Schema에 report_id가 required인지 점검합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    raise NotImplementedError('D29-03-A-04: 직접 구현하세요')

