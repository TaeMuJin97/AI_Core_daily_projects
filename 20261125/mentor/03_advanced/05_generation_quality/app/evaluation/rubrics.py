"""Day28 실습 05 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def label_answer_quality(relevance: str, correctness: str) -> dict:
    """질문 적합성(Relevance)과 정답성(Correctness)을 별도 필드로 보존하세요."""
    # 정답 D28-05-A03: 질문 적합성(Relevance)과 정답성(Correctness)을 별도 필드로 보존하세요.
    # 절차: 근거와 일치해도 질문에 답하지 않았으면 적합성이 낮을 수 있습니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    valid_r={'높음','보통','낮음','평가 보류'}
    valid_c={'정답','부분정답','오답','판정 불가'}
    if relevance not in valid_r or correctness not in valid_c:
        raise ValueError('판정 값이 정해진 Rubric 밖입니다.')
    return {'answer_relevance':relevance,'answer_correctness':correctness}

