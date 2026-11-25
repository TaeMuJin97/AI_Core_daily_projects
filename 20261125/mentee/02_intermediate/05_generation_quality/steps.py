"""Day28 실습 05 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def claim_faithfulness(claims: list[dict]) -> float | None:
    """Claim 목록에서 근거가 지지하는 Claim 비율을 계산하세요. Claim이 없으면 None."""
    # TODO D28-05-I01: Claim 목록에서 근거가 지지하는 Claim 비율을 계산하세요. Claim이 없으면 None.
    # 힌트: 모든 Claim의 supported는 교육용 사람 레이블입니다.
    raise NotImplementedError("D28-05-I01 TODO를 완성하세요")

def describe_claim_result(claims: list[dict]) -> str:
    """비지원 Claim을 이름과 함께 기록하세요. “모든 Claim 지원”과 “Claim 없음”은 구별합니다."""
    # TODO D28-05-I02: 비지원 Claim을 이름과 함께 기록하세요. “모든 Claim 지원”과 “Claim 없음”은 구별합니다.
    # 힌트: Faithfulness는 Reference Answer와의 비교가 아닙니다.
    raise NotImplementedError("D28-05-I02 TODO를 완성하세요")

