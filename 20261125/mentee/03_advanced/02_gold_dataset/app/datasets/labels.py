"""Day28 실습 02 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def select_gold(question_id: str, gold: dict) -> list[str]:
    """gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요."""
    # TODO D28-02-A01: gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요.
    # 힌트: Gold는 Retriever의 정답이 아니라 평가용 레이블입니다.
    raise NotImplementedError("D28-02-A01 TODO를 완성하세요")

def validate_gold_ids(ids: list[str], corpus: dict) -> bool:
    """ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요."""
    # TODO D28-02-A02: ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요.
    # 힌트: set의 길이와 corpus.keys()를 활용하세요.
    raise NotImplementedError("D28-02-A02 TODO를 완성하세요")

