"""전 단계의 Idea 예제. 이 파일은 입력이 계약에 맞다는 전제로 상태를 묶습니다."""
class Idea:
    def __init__(self, name, problem, roles, difficulty):
        # 제공 코드 INIT: name·problem의 공백을 제거하고 roles를 새 List로 복사해 네 속성을 저장하세요.
        self.name = name.strip()
        self.problem = problem.strip()
        # 원소가 문자열이므로 바깥 List의 얕은 복사로 충분합니다.
        self.roles = list(roles)
        self.difficulty = difficulty.strip()

    def summary(self):
        # 제공 코드 SUMMARY: '이름: 역할 N개' 형태의 문자열을 반환하세요. print하지 않습니다.
        return f"{self.name}: 역할 {len(self.roles)}개"

    def add_role(self, role):
        # TODO ADD-ROLE: 문자열 공백 제거·빈 값 검사·대소문자 무시 중복 검사 후 True/False를 반환하세요.
        raise NotImplementedError("TODO ADD-ROLE")

def main():
    idea = Idea("문서 도우미", "검색", ["Researcher"], "응용")
    print(idea.add_role(" Writer "))
    print(idea.add_role("writer"))
    try:
        idea.add_role("   ")
    except ValueError:
        print("빈 역할 거부")
    print(idea.roles)
    print(idea.summary())

if __name__ == "__main__":
    main()
