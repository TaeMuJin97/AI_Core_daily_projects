"""Day28 실습 04 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def first_relevant_rank(ranked: list[str], gold: list[str], k: int) -> int | None:
    """Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None."""
    # 정답 D28-04-I01: Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None.
    # 절차: enumerate(..., start=1)을 활용하세요.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    for pos,cid in enumerate(ranked[:k],1):
        if cid in gold:
            return pos
    return None

def calculate_rr(position: int | None) -> float:
    """관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다."""
    # 정답 D28-04-I02: 관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다.
    # 절차: Gold가 아예 없는 No-answer 사례는 집계 대상에서 제외합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return 1.0/position if position is not None else 0.0

