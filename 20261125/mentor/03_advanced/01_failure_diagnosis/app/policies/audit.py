"""Day28 실습 01 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def audit_decision(case: dict, stage: str, evidence: str) -> dict:
    """원래 case_id·분류·증거를 감사 기록으로 보존하되, 원본 Prompt·비밀값을 출력하지 않는 dict를 만드세요."""
    # 정답 D28-01-A04: 원래 case_id·분류·증거를 감사 기록으로 보존하되, 원본 Prompt·비밀값을 출력하지 않는 dict를 만드세요.
    # 절차: 오류 원문을 외부 응답으로 그대로 전달하지 않습니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return {
        'case_id':str(case['case_id']),
        'stage':stage,
        'evidence':evidence,
        'recorded':True,
        'safe_message':'문제 단계 확인 완료',
    }

