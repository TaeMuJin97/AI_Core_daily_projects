"""등록·조회 책임. 사용자 입력과 화면 출력은 main.py에서 처리합니다."""
class IdeaCatalog:
    def __init__(self):
        # TODO CATALOG-INIT: 객체마다 독립적인 ideas List를 만드세요.
        raise NotImplementedError("TODO CATALOG-INIT")
    def add(self, idea):
        # TODO CATALOG-ADD: 전달받은 Idea를 현재 목록에 추가하세요.
        raise NotImplementedError("TODO CATALOG-ADD")
    def names(self):
        # TODO CATALOG-NAMES: 객체 목록을 순회해 이름 List를 반환하세요.
        raise NotImplementedError("TODO CATALOG-NAMES")
