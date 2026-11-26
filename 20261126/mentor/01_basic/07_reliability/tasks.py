"""07 · Tool 실패·권한·반복 상한 · 기본필수 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def validate_report_id(value) -> int:
    """invalid args는 DB 쿼리 전에 차단합니다."""
    # 해설 D29-07-B-01: 입력 오류, 권한 정책 위반, DB/모델 장애는 서로 다른 오류 경계입니다.
    # 검수 기준: 호출 제한과 최소 감사로그로 비정상 반복·기밀값 노출을 차단합니다.
    from coursekit.contracts import report_id_from
    return report_id_from(value)

def classify_error(exc: Exception) -> dict:
    """사용자 입력 오류와 연결 오류를 구분. 비밀정보·SQL 원문 로그 노출 금지."""
    # 해설 D29-07-B-02: 입력 오류, 권한 정책 위반, DB/모델 장애는 서로 다른 오류 경계입니다.
    # 검수 기준: 호출 제한과 최소 감사로그로 비정상 반복·기밀값 노출을 차단합니다.
    return {'status':'error','error_code':'INVALID_ARGS' if isinstance(exc,ValueError) else 'TOOL_FAILURE'}

