"""Day28 실습 07 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def compare_four_variants(runs: dict, gold: list[str], grades: dict) -> dict:
    """Baseline, Rewrite Only, Rerank Only, Both를 같은 Gold와 k로 평가한 딕셔너리를 만드세요."""
    # 정답 D28-07-I03: Baseline, Rewrite Only, Rerank Only, Both를 같은 Gold와 k로 평가한 딕셔너리를 만드세요.
    # 절차: 한 번에 하나의 기능을 바꾼 비교군을 남기는 이유를 해설하세요.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_metrics import evaluate_retrieval
    return {name:evaluate_retrieval(item['ranked_ids'],gold,grades,k=3)
            for name,item in runs.items()}

