"""Day28 실습 05 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def prepare_human_review(case_id: str, score: float | None, reviewer: str) -> dict:
    """모델 자동 판정이 아닌 사람 검수 레이블임을 표시하고, 이견 검토 상태를 남기는 기록을 작성하세요."""
    # 정답 D28-05-A04: 모델 자동 판정이 아닌 사람 검수 레이블임을 표시하고, 이견 검토 상태를 남기는 기록을 작성하세요.
    # 절차: LLM Judge 결과만으로 임의의 규정/의료/금융 답변을 확정하지 않습니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return {'case_id':case_id,'faithfulness':score,
            'judge':'human_fixture','reviewer':reviewer,
            'disagreement':'추가 사람 검토 필요','publishable':False}

