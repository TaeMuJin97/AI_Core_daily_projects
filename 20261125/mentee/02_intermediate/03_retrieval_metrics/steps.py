"""Day28 실습 03 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def calculate_recall(ranked: list[str], gold: list[str], k: int) -> float | None:
    """Top-k에서 찾은 Gold 개수 / 전체 Gold 개수를 계산하세요. Gold가 빈 질문은 None을 반환하세요."""
    # TODO D28-03-I01: Top-k에서 찾은 Gold 개수 / 전체 Gold 개수를 계산하세요. Gold가 빈 질문은 None을 반환하세요.
    # 힌트: 예: Gold 2개 중 Top-3에 1개면 Recall@3=0.5입니다.
    raise NotImplementedError("D28-03-I01 TODO를 완성하세요")

def count_gold_hits(ranked: list[str], gold: list[str], k: int) -> int:
    """Top-k 목록과 Gold의 교집합 크기를 반환하세요. 중복 ID는 한 번만 셉니다."""
    # TODO D28-03-I02: Top-k 목록과 Gold의 교집합 크기를 반환하세요. 중복 ID는 한 번만 셉니다.
    # 힌트: set 교집합(&)을 사용할 수 있습니다.
    raise NotImplementedError("D28-03-I02 TODO를 완성하세요")

