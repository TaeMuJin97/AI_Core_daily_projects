"""Day28 실습 07 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def score_delta(before: float | None, after: float | None) -> float | None:
    """같은 질문의 Before/After 점수 변화량을 계산하세요. No-answer(None)는 수치 차이를 만들지 않습니다."""
    # 정답 D28-07-I01: 같은 질문의 Before/After 점수 변화량을 계산하세요. No-answer(None)는 수치 차이를 만들지 않습니다.
    # 절차: A/B 비교 전 두 실행의 Dataset 버전과 모드가 같아야 합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    if before is None or after is None:
        return None
    return round(after-before,6)

def find_problem_stage(run: dict, gold: list[str]) -> str:
    """검색 후보 누락·Reranking 누락·Context 누락·생성 실패 중 어디인지 반환하세요."""
    # 정답 D28-07-I02: 검색 후보 누락·Reranking 누락·Context 누락·생성 실패 중 어디인지 반환하세요.
    # 절차: Candidate에 Gold가 없다면 먼저 Retrieval 단계 문제입니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_experiments import diagnose
    return diagnose(run,gold)

