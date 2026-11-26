"""경계값·오류/권한 정책: Advanced · Day29."""

def validate_message_pair(call: dict, message: dict) -> bool:
    """두 메시지에 같은 호출 ID·Tool 이름이 들어 있는지 확인."""
    # TODO D29-02-A-03: 두 메시지에 같은 호출 ID·Tool 이름이 들어 있는지 확인.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.
    raise NotImplementedError('D29-02-A-03: 직접 구현하세요')

def summarize_pairs(calls: list[dict], messages: list[dict]) -> dict:
    """복수 Tool Call의 ID 매칭 누락/중복을 보고합니다."""
    # TODO D29-02-A-04: 복수 Tool Call의 ID 매칭 누락/중복을 보고합니다.
    # 힌트: name, args, id가 요청값이고 tool_call_id가 결과의 연결 키입니다.
    raise NotImplementedError('D29-02-A-04: 직접 구현하세요')

