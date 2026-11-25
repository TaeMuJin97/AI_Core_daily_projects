"""Day28 실습 02 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def label_no_answer(question_id: str, gold: dict) -> bool:
    """Gold가 비어 있는 질문은 No-answer로 분리하는 bool을 반환하세요."""
    # 정답 D28-02-A03: Gold가 비어 있는 질문은 No-answer로 분리하는 bool을 반환하세요.
    # 절차: Gold가 없는 질문의 Recall을 0점으로 평균내면 안 됩니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return len(gold[question_id])==0

