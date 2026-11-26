"""용도별 추가 검증: Intermediate · Day29."""

def tool_budget_check(calls: int, maximum: int) -> bool:
    """최대 호출 수를 넘기면 False(실패). 무한 반복 금지."""
    # 해설 D29-07-I-03: 입력 오류, 권한 정책 위반, DB/모델 장애는 서로 다른 오류 경계입니다.
    # 검수 기준: 호출 제한과 최소 감사로그로 비정상 반복·기밀값 노출을 차단합니다.
    if maximum<1 or calls<0:raise ValueError('invalid limit counters')
    return calls<=maximum

