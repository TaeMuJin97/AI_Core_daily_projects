"""용도별 추가 검증: Intermediate · Day29."""

def summarize_tool_messages(messages: list) -> dict:
    """Model 요청 수와 실제 ToolMessage 수를 별도로 집계."""
    # 해설 D29-06-I-03: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    from coursekit.contracts import count_tool_calls
    return count_tool_calls(messages)

