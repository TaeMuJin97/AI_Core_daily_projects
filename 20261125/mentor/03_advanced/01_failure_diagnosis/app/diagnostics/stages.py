"""Day28 실습 01 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def classify_case(case: dict) -> str:
    """case의 system_error·candidate_has_gold·context_has_gold·answer_grounded를 차례로 확인하고 stage 문자열을 반환하세요. 시스템 장애와 검색 실패를 구분하세요."""
    # 정답 D28-01-A01: case의 system_error·candidate_has_gold·context_has_gold·answer_grounded를 차례로 확인하고 stage 문자열을 반환하세요. 시스템 장애와 검색 실패를 구분하세요.
    # 절차: 먼저 System → Candidate → Context → Generation 순서로 판단합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    if case.get('system_error'):
        return 'system_failure'
    if not case.get('candidate_has_gold'):
        return 'candidate_miss'
    if not case.get('context_has_gold'):
        return 'ranking_or_context_miss'
    if not case.get('answer_grounded'):
        return 'generation_failure'
    return 'passed'

def describe_evidence(case: dict, stage: str) -> str:
    """분류된 stage를 설명할 수 있는 구체적인 한 줄의 근거를 반환하세요. 빈 문자열은 안 됩니다."""
    # 정답 D28-01-A02: 분류된 stage를 설명할 수 있는 구체적인 한 줄의 근거를 반환하세요. 빈 문자열은 안 됩니다.
    # 절차: 후보 누락과 Context 누락을 구별하는 문장으로 작성합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    evidence = {
        'system_failure':'서비스 실행이 실패해 지표를 계산할 수 없음',
        'candidate_miss':'Gold 문서 ID가 최초 검색 후보에 존재하지 않음',
        'ranking_or_context_miss':'Gold는 후보에 있으나 LLM Context에 포함되지 않음',
        'generation_failure':'근거가 Context에 있는데 답변 주장이 지지되지 않음',
        'passed':'검색 후보·Context·답변 검토 조건 충족',
    }
    return evidence[stage]

