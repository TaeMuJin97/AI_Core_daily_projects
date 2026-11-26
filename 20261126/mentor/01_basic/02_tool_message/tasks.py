"""02 · AIMessage.tool_calls / ToolMessage · 기본필수 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def make_request(tool_name: str, args: dict, call_id: str) -> dict:
    """AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다."""
    # 해설 D29-02-B-01: Tool Call은 요청 dict이고 실제 DB 조회가 끝난 뒤 결과 메시지가 생성됩니다.
    # 검수 기준: 같은 ID로 요청과 결과를 연결하고, 다중 호출에는 중복·누락 검사를 적용합니다.
    from coursekit.contracts import tool_call_request
    return tool_call_request(tool_name,args,call_id)

def match_result(call: dict, result: dict) -> dict:
    """실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다."""
    # 해설 D29-02-B-02: Tool Call은 요청 dict이고 실제 DB 조회가 끝난 뒤 결과 메시지가 생성됩니다.
    # 검수 기준: 같은 ID로 요청과 결과를 연결하고, 다중 호출에는 중복·누락 검사를 적용합니다.
    from coursekit.contracts import tool_result_message
    return tool_result_message(call,result)

