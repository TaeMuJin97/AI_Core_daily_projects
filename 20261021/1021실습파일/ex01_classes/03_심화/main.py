"""전 단계의 Idea 예제. 이 파일은 입력이 계약에 맞다는 전제로 상태를 묶습니다."""
class Idea:
    def __init__(self, name, problem, roles, difficulty):
        # TODO INIT: name·problem의 공백을 제거하고 roles를 새 List로 복사해 네 속성을 저장하세요.
        raise NotImplementedError("TODO INIT")

    def summary(self):
        # TODO SUMMARY: '이름: 역할 N개' 형태의 문자열을 반환하세요. print하지 않습니다.
        raise NotImplementedError("TODO SUMMARY")


class InputSharedIdea:
    """의도적인 잘못된 예제 1: 이 클래스를 실무에 그대로 사용하지 않습니다."""
    def __init__(self, roles):
        self.roles = roles

class ClassSharedIdea:
    """의도적인 잘못된 예제 2: 모든 객체가 같은 List를 참조합니다."""
    roles = []

def main():
    original = ["Researcher"]
    wrong_first = InputSharedIdea(original)
    wrong_second = InputSharedIdea(original)
    wrong_first.roles.append("Writer")
    print("입력 List 공유:", wrong_second.roles)
    ClassSharedIdea.roles.clear()  # 재현을 반복해도 같은 시작 상태
    a, b = ClassSharedIdea(), ClassSharedIdea()
    a.roles.append("Writer")
    print("클래스 속성 공유:", b.roles)
    original = ["Researcher"]
    first = Idea("문서", "검색", original, "응용")
    second = Idea("학습", "복습", original, "기본필수")
    first.roles.append("Writer")
    original.append("Planner")
    print("수정 후 객체 1:", first.roles)
    print("수정 후 객체 2:", second.roles)
    print("입력 List:", original)

if __name__ == "__main__":
    main()
