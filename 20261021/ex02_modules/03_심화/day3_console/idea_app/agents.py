"""상속·다형성 학습용 규칙 기반 역할. 모델·네트워크를 사용하지 않습니다."""
class Agent:
    def run(self, task):
        # 추상 계약 표시: 의도된 NotImplementedError이며 학생 TODO가 아닙니다.
        raise NotImplementedError("자식 클래스가 run을 구현해야 합니다")

class Researcher(Agent):
    def run(self, task):
        # TODO RESEARCHER: '검색: 작업명'을 반환하세요. 화면에 직접 출력하지 않습니다.
        raise NotImplementedError("TODO RESEARCHER")

class Writer(Agent):
    def run(self, task):
        # TODO WRITER: '작성: 작업명'을 반환하세요. run(task) 계약을 지킵니다.
        raise NotImplementedError("TODO WRITER")

def run_roles(agents, task):
    # TODO DISPATCH: 구체적인 클래스 이름을 검사하지 말고 각 객체의 run(task)를 호출해 결과 List를 반환하세요.
    raise NotImplementedError("TODO DISPATCH")
