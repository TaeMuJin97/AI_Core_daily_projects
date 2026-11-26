"""용도별 추가 검증: Intermediate · Day29."""

def status_is_usable(raw: dict) -> bool:
    """ready 문자열 하나가 아닌 vector_fresh까지 확인합니다."""
    # 해설 D29-05-I-03: 보고서 상태는 pending/ready/failed이고 제출 여부가 아닙니다.
    # 검수 기준: ready 문자열뿐 아니라 Model·Revision·Overview Hash가 일치하는지 검증합니다.
    return raw.get('status')=='ok' and raw.get('index_status')=='ready' and raw.get('vector_fresh') is True

