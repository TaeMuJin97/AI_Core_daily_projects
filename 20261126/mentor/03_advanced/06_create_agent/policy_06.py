"""경계값·오류/권한 정책: Advanced · Day29."""

def summarize_tool_messages(messages: list) -> dict:
    """Model 요청 수와 실제 ToolMessage 수를 별도로 집계."""
    # 해설 D29-06-A-03: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    from coursekit.contracts import count_tool_calls
    return count_tool_calls(messages)

def final_text(messages: list) -> str:
    """ToolMessage가 아니라 최종 AIMessage의 텍스트를 추출합니다."""
    # 해설 D29-06-A-04: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    for m in reversed(messages):
        if m.__class__.__name__=='AIMessage' and not getattr(m,'tool_calls',[]):
            if isinstance(m.content,str):return m.content
            raise ValueError('최종 응답은 문자열이 아닙니다. Structured Output 파서 필요.')
    raise ValueError('최종 AIMessage가 없습니다.')

