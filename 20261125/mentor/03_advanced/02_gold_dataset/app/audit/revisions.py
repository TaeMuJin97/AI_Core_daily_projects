"""Day28 실습 02 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def audit_gold(question_id: str, ids: list[str], version: str) -> dict:
    """question_id·Gold ID·데이터셋 버전·고정 여부를 포함하는 감사 기록을 만드세요. 평가 결과로 Gold를 수정하지 않습니다."""
    # 정답 D28-02-A04: question_id·Gold ID·데이터셋 버전·고정 여부를 포함하는 감사 기록을 만드세요. 평가 결과로 Gold를 수정하지 않습니다.
    # 절차: 현재 레이블은 실제 기관 전문가의 판정이 아닌 교육용 예시입니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return {'question_id':question_id,'gold_chunk_ids':list(ids),
            'gold_version':version,'frozen':True,
            'review_status':'교육용 사전 검토 레이블'}

