"""Day28 실습 02 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def select_gold(question_id: str, gold: dict) -> list[str]:
    """gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요."""
    # 정답 D28-02-I01: gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요.
    # 절차: Gold는 Retriever의 정답이 아니라 평가용 레이블입니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    ids=list(gold[question_id])
    return list(dict.fromkeys(ids))

def validate_gold_ids(ids: list[str], corpus: dict) -> bool:
    """ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요."""
    # 정답 D28-02-I02: ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요.
    # 절차: set의 길이와 corpus.keys()를 활용하세요.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return len(ids)==len(set(ids)) and all(cid in corpus for cid in ids)

