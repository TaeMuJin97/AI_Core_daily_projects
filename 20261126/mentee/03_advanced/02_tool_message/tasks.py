"""02 · AIMessage.tool_calls / ToolMessage · 심화 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def make_request(tool_name: str, args: dict, call_id: str) -> dict:
    """AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다."""
    # TODO D29-02-A-01: AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.
    raise NotImplementedError('D29-02-A-01: 직접 구현하세요')

def match_result(call: dict, result: dict) -> dict:
    """실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다."""
    # TODO D29-02-A-02: 실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.
    raise NotImplementedError('D29-02-A-02: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from policy_02 import validate_message_pair, summarize_pairs
