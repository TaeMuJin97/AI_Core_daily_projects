"""Day28 실습 01 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def classify_case(case: dict) -> str:
    """case의 system_error·candidate_has_gold·context_has_gold·answer_grounded를 차례로 확인하고 stage 문자열을 반환하세요. 시스템 장애와 검색 실패를 구분하세요."""
    # TODO D28-01-A01: case의 system_error·candidate_has_gold·context_has_gold·answer_grounded를 차례로 확인하고 stage 문자열을 반환하세요. 시스템 장애와 검색 실패를 구분하세요.
    # 힌트: 먼저 System → Candidate → Context → Generation 순서로 판단합니다.
    raise NotImplementedError("D28-01-A01 TODO를 완성하세요")

def describe_evidence(case: dict, stage: str) -> str:
    """분류된 stage를 설명할 수 있는 구체적인 한 줄의 근거를 반환하세요. 빈 문자열은 안 됩니다."""
    # TODO D28-01-A02: 분류된 stage를 설명할 수 있는 구체적인 한 줄의 근거를 반환하세요. 빈 문자열은 안 됩니다.
    # 힌트: 후보 누락과 Context 누락을 구별하는 문장으로 작성합니다.
    raise NotImplementedError("D28-01-A02 TODO를 완성하세요")

