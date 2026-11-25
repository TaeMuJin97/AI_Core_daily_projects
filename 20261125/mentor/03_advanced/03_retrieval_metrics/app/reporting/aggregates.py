"""Day28 실습 03 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def summarize_valid_recall(values: list[float | None]) -> dict:
    """None을 평균에서 제외하고 평균과 포함·제외 질문 개수를 함께 보고하세요."""
    # 정답 D28-03-A04: None을 평균에서 제외하고 평균과 포함·제외 질문 개수를 함께 보고하세요.
    # 절차: 빈 목록이면 mean_recall=None으로 처리합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    valid=[v for v in values if v is not None]
    return {'mean_recall':sum(valid)/len(valid) if valid else None,
            'evaluated_count':len(valid),'excluded_no_answer':len(values)-len(valid)}

