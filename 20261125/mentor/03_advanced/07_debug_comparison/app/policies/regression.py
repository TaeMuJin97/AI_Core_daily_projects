"""Day28 실습 07 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def regression_decision(before: float | None, after: float | None, error_count: int) -> dict:
    """Baseline보다 Recall이 감소하거나 오류가 있으면 배포 보류를 반환하고 이유를 기록하세요."""
    # 정답 D28-07-A04: Baseline보다 Recall이 감소하거나 오류가 있으면 배포 보류를 반환하고 이유를 기록하세요.
    # 절차: 이 단계의 Gate만 통과했다고 실제 배포 승인이 되는 것은 아닙니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    regression=(before is not None and after is not None and after<before)
    return {'regression':regression,'error_count':error_count,
            'hold_release':regression or error_count>0,
            'reason':'회귀/오류 발견' if regression or error_count>0 else '추가 사람 평가 필요'}

