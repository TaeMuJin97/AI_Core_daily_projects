"""03 · @tool·Pydantic·JSON Schema · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def validate_id(report_id: int) -> int:
    """실제 reports.report_id인 양의 정수만 허용합니다."""
    # TODO D29-03-B-01: 실제 reports.report_id인 양의 정수만 허용합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    raise NotImplementedError('D29-03-B-01: 직접 구현하세요')

def register_status_tool():
    """@tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다."""
    # TODO D29-03-B-02: @tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    raise NotImplementedError('D29-03-B-02: 직접 구현하세요')

