"""경계값·오류/권한 정책: Advanced · Day29."""

def summarize_tool_messages(messages: list) -> dict:
    """Model 요청 수와 실제 ToolMessage 수를 별도로 집계."""
    # TODO D29-06-A-03: Model 요청 수와 실제 ToolMessage 수를 별도로 집계.
    # 힌트: create_agent에 두 Tool을 등록하고 AIMessage와 ToolMessage를 구별하세요.
    raise NotImplementedError('D29-06-A-03: 직접 구현하세요')

def final_text(messages: list) -> str:
    """ToolMessage가 아니라 최종 AIMessage의 텍스트를 추출합니다."""
    # TODO D29-06-A-04: ToolMessage가 아니라 최종 AIMessage의 텍스트를 추출합니다.
    # 힌트: create_agent에 두 Tool을 등록하고 AIMessage와 ToolMessage를 구별하세요.
    raise NotImplementedError('D29-06-A-04: 직접 구현하세요')

