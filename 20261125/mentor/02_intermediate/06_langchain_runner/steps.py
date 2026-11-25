"""Day28 실습 06 · 02_intermediate · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def safe_target_input(example: dict) -> dict:
    """question_id·question·category·history만 새 dict로 복사하고 Gold·Reference를 제외하세요."""
    # 정답 D28-06-I01: question_id·question·category·history만 새 dict로 복사하고 Gold·Reference를 제외하세요.
    # 절차: Target Runner는 정답을 모르는 상태에서 실행해야 공정합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    # Gold Label 및 Reference Answer는 모델 입력으로 전달하지 않습니다.
    return {key:example[key] for key in ('question_id','question','category','history')}

def invoke_target(target, request: dict) -> dict:
    """실제 Runnable.invoke(request)를 호출하고 결과가 dict이며 질문 ID가 같은지 확인하세요."""
    # 정답 D28-06-I02: 실제 Runnable.invoke(request)를 호출하고 결과가 dict이며 질문 ID가 같은지 확인하세요.
    # 절차: 단순 함수 직접 호출 대신 RunnableLambda를 감싼 객체의 invoke()입니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_dataset import assert_no_gold_leakage
    assert_no_gold_leakage(request)
    result=target.invoke(request)
    if not isinstance(result,dict) or result.get('question_id')!=request['question_id']:
        raise ValueError('Target 출력의 질문 ID 불일치')
    return result

