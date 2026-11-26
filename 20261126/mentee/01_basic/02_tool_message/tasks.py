"""02 · AIMessage.tool_calls / ToolMessage · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
import json


def make_request(tool_name: str, args: dict, call_id: str) -> dict:
    """AIMessage.tool_calls의 항목 형태. 실제로 도구를 실행하지는 않습니다."""
    # TODO D29-02-B-01
    # [흐름 이해: 모델이 반환하는 AIMessage.tool_calls의 단일 요청(ToolCall) 객체 구성]
    # 1) tool_name과 call_id는 비어 있지 않은 문자열, args는 dict여야 합니다.
    # 2) 원본 args가 외부에서 수정되어도 요청 객체가 오염되지 않도록 dict(args)로 얕은 복사합니다.
    # 3) 여기서는 요청 데이터만 만들 뿐, 실제 DB 조회나 Python Tool 실행은 일어나지 않습니다.
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name은 비어 있지 않은 문자열이어야 합니다.")
    if not isinstance(args, dict):
        raise TypeError("args는 dict 형식이어야 합니다.")
    if not isinstance(call_id, str) or not call_id.strip():
        raise ValueError("call_id는 비어 있지 않은 문자열이어야 합니다.")

    return {
        "name": tool_name.strip(),
        "args": dict(args),
        "id": call_id.strip(),
        "type": "tool_call",
    }


def match_result(call: dict, result: dict) -> dict:
    """실제로 DB Tool을 호출한 뒤 결과를 같은 tool_call_id에 묶습니다."""
    # TODO D29-02-B-02
    # [흐름 이해: 실제 Tool 실행 결과를 요청 ID(call['id'])와 연결한 ToolMessage 형태 구성]
    # 1) call에 필수 키('id', 'name')가 있는지 검증합니다.
    # 2) call['id']를 결과 메시지의 'tool_call_id'로 연결해 어떤 요청의 응답인지 명확히 매칭합니다.
    # 3) 실제 DB 조회 결과(result)는 LangChain ToolMessage 규격에 맞게 JSON 문자열(content)로 직렬화합니다.
    if not isinstance(call, dict):
        raise TypeError("call은 make_request()가 반환한 dict여야 합니다.")
    if not isinstance(result, dict):
        raise TypeError("result는 실제 Tool 실행 결과 dict여야 합니다.")

    call_id = call.get("id")
    tool_name = call.get("name")
    if not isinstance(call_id, str) or not call_id.strip():
        raise ValueError("call에 유효한 'id' 필드가 필요합니다.")
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("call에 유효한 'name' 필드가 필요합니다.")

    return {
        "type": "tool",
        "name": tool_name.strip(),
        "tool_call_id": call_id.strip(),
        "content": json.dumps(result, ensure_ascii=False),
    }