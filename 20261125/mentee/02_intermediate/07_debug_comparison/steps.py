"""Day28 실습 07 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def score_delta(before: float | None, after: float | None) -> float | None:
    """같은 질문의 Before/After 점수 변화량을 계산하세요. No-answer(None)는 수치 차이를 만들지 않습니다."""
    # TODO D28-07-I01: 같은 질문의 Before/After 점수 변화량을 계산하세요. No-answer(None)는 수치 차이를 만들지 않습니다.
    # 힌트: A/B 비교 전 두 실행의 Dataset 버전과 모드가 같아야 합니다.
    raise NotImplementedError("D28-07-I01 TODO를 완성하세요")

def find_problem_stage(run: dict, gold: list[str]) -> str:
    """검색 후보 누락·Reranking 누락·Context 누락·생성 실패 중 어디인지 반환하세요."""
    # TODO D28-07-I02: 검색 후보 누락·Reranking 누락·Context 누락·생성 실패 중 어디인지 반환하세요.
    # 힌트: Candidate에 Gold가 없다면 먼저 Retrieval 단계 문제입니다.
    raise NotImplementedError("D28-07-I02 TODO를 완성하세요")

