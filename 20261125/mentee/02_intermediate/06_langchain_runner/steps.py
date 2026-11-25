"""Day28 실습 06 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def safe_target_input(example: dict) -> dict:
    """question_id·question·category·history만 새 dict로 복사하고 Gold·Reference를 제외하세요."""
    # TODO D28-06-I01: question_id·question·category·history만 새 dict로 복사하고 Gold·Reference를 제외하세요.
    # 힌트: Target Runner는 정답을 모르는 상태에서 실행해야 공정합니다.
    raise NotImplementedError("D28-06-I01 TODO를 완성하세요")

def invoke_target(target, request: dict) -> dict:
    """실제 Runnable.invoke(request)를 호출하고 결과가 dict이며 질문 ID가 같은지 확인하세요."""
    # TODO D28-06-I02: 실제 Runnable.invoke(request)를 호출하고 결과가 dict이며 질문 ID가 같은지 확인하세요.
    # 힌트: 단순 함수 직접 호출 대신 RunnableLambda를 감싼 객체의 invoke()입니다.
    raise NotImplementedError("D28-06-I02 TODO를 완성하세요")

