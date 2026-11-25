"""Day28 실습 04 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def calculate_ndcg(ranked: list[str], grades: dict[str,int], k: int) -> float | None:
    """Gold 등급에서 이상적인 순서를 만들어 IDCG를 구한 다음 DCG/IDCG를 계산하세요. Gold가 비었으면 None."""
    # 정답 D28-04-A04: Gold 등급에서 이상적인 순서를 만들어 IDCG를 구한 다음 DCG/IDCG를 계산하세요. Gold가 비었으면 None.
    # 절차: 등급이 높을수록 앞순위에 오도록 정렬합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from math import log2
    if not grades:
        return None
    if any(cid not in grades for cid in ranked[:k]):
        raise ValueError("미판정 후보의 등급을 먼저 확인하세요")
    ideal=sorted(grades,key=lambda cid:(-grades[cid],cid))
    def dcg(items):
        return sum((2**grades[cid]-1)/log2(i+2) for i,cid in enumerate(items[:k]))
    optimal=dcg(ideal)
    return dcg(ranked)/optimal if optimal>0 else None

