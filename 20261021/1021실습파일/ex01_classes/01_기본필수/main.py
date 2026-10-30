"""전 단계의 Idea 예제. 이 파일은 입력이 계약에 맞다는 전제로 상태를 묶습니다."""
class Idea:
    def __init__(self, name, problem, roles, difficulty):
        # TODO INIT: name·problem의 공백을 제거하고 roles를 새 List로 복사해 네 속성을 저장하세요.
        raise NotImplementedError("TODO INIT")

    def summary(self):
        # TODO SUMMARY: '이름: 역할 N개' 형태의 문자열을 반환하세요. print하지 않습니다.
        raise NotImplementedError("TODO SUMMARY")


def main():
    first = Idea("문서 도우미", "자료 찾기", ["Researcher", "Writer"], "응용")
    second = Idea("학습 도우미", "복습", ["Tutor"], "기본필수")
    print(first.summary())
    print(second.summary())

if __name__ == "__main__":
    main()
