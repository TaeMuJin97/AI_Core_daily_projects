"""용도별 추가 검증: Intermediate · Day29."""

def validate_message_pair(call: dict, message: dict) -> bool:
    """두 메시지에 같은 호출 ID·Tool 이름이 들어 있는지 확인."""
    # 해설 D29-02-I-03: Tool Call은 요청 dict이고 실제 DB 조회가 끝난 뒤 결과 메시지가 생성됩니다.
    # 검수 기준: 같은 ID로 요청과 결과를 연결하고, 다중 호출에는 중복·누락 검사를 적용합니다.
    return call['id']==message['tool_call_id'] and call['name']==message['name']

