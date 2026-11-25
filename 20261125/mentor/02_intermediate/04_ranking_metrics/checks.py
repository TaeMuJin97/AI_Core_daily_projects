"""Day28 실습 04 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def calculate_dcg(ranked: list[str], grades: dict[str,int], k: int) -> float:
    """DCG@k를 Σ(2^grade-1)/log2(rank+1)로 계산하세요. 없는 문서 등급은 0."""
    # 정답 D28-04-I03: DCG@k를 Σ(2^grade-1)/log2(rank+1)로 계산하세요. 없는 문서 등급은 0.
    # 절차: nDCG 정규화 전에 순위별 DCG 기여도를 합산합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from math import log2
    if any(cid not in grades for cid in ranked[:k]):
        raise ValueError("미판정 후보의 등급을 먼저 확인하세요")
    return sum((2**grades[cid]-1)/log2(position+1)
               for position,cid in enumerate(ranked[:k],1))

