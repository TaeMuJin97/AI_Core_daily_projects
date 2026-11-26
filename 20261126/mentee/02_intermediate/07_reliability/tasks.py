"""07 · Tool 실패·권한·반복 상한 · 응용 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def validate_report_id(value) -> int:
    """invalid args는 DB 쿼리 전에 차단합니다."""
    # TODO D29-07-I-01: invalid args는 DB 쿼리 전에 차단합니다.
    # 힌트: 오류 코드를 구분하고 호출 상한 초과를 성공으로 처리하지 마세요.
    raise NotImplementedError('D29-07-I-01: 직접 구현하세요')

def classify_error(exc: Exception) -> dict:
    """사용자 입력 오류와 연결 오류를 구분. 비밀정보·SQL 원문 로그 노출 금지."""
    # TODO D29-07-I-02: 사용자 입력 오류와 연결 오류를 구분. 비밀정보·SQL 원문 로그 노출 금지.
    # 힌트: 오류 코드를 구분하고 호출 상한 초과를 성공으로 처리하지 마세요.
    raise NotImplementedError('D29-07-I-02: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_07 import tool_budget_check
