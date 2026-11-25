"""Day28 실습 08 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def evaluate_one(example: dict, run: dict, gold: list[str], grades: dict) -> dict:
    """질문 ID로 Target 출력과 Gold를 결합해 평가 레코드를 반환하세요."""
    # TODO D28-08-A01: 질문 ID로 Target 출력과 Gold를 결합해 평가 레코드를 반환하세요.
    # 힌트: Trace 필드가 빠졌다면 빈 리스트로 바꾸지 말고 오류로 보고합니다.
    raise NotImplementedError("D28-08-A01 TODO를 완성하세요")

def summarize_all(rows: list[dict]) -> dict:
    """개별 질문 결과의 평균(유효 Gold만)과 오류·출처 상태를 집계하세요."""
    # TODO D28-08-A02: 개별 질문 결과의 평균(유효 Gold만)과 오류·출처 상태를 집계하세요.
    # 힌트: No-answer 질문은 Retrieval 평균에서 제외하고 별도 개수로 기록합니다.
    raise NotImplementedError("D28-08-A02 TODO를 완성하세요")

