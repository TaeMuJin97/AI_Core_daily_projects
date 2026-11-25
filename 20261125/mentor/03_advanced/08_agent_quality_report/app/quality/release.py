"""Day28 실습 08 · 03_advanced · 함수 역할별 구현.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""

def agent_release_gate(summary: dict, human_ok: bool, access_ok: bool) -> dict:
    """Recall·MRR·출처·실행 상태와 사람 검토·접근제어를 함께 검사하는 1차 Agent 준비 Gate를 반환하세요."""
    # 정답 D28-08-A04: Recall·MRR·출처·실행 상태와 사람 검토·접근제어를 함께 검사하는 1차 Agent 준비 Gate를 반환하세요.
    # 절차: 1차 Gate는 실서비스 배포 전 모든 보안·운영 점검을 대체하지 않습니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_report import release_gate
    return release_gate({**summary,'human_review_passed':bool(human_ok),
                         'access_control_passed':bool(access_ok)},
                        min_recall=.70,min_mrr=.60)

