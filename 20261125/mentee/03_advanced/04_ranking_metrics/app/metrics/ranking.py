"""Day28 실습 04 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def first_relevant_rank(ranked: list[str], gold: list[str], k: int) -> int | None:
    """Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None."""
    # TODO D28-04-A01: Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None.
    # 힌트: enumerate(..., start=1)을 활용하세요.
    raise NotImplementedError("D28-04-A01 TODO를 완성하세요")

def calculate_rr(position: int | None) -> float:
    """관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다."""
    # TODO D28-04-A02: 관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다.
    # 힌트: Gold가 아예 없는 No-answer 사례는 집계 대상에서 제외합니다.
    raise NotImplementedError("D28-04-A02 TODO를 완성하세요")

