"""05 · PostgreSQL Read-only lookup_status · 심화 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def parse_report_id(value) -> int:
    """task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다."""
    # TODO D29-05-A-01: task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다.
    # 힌트: index_status는 DB 인덱싱 상태이며 vector_fresh는 별도 검사 값입니다.
    raise NotImplementedError('D29-05-A-01: 직접 구현하세요')

def status_view(raw: dict) -> dict:
    """pending/ready/failed와 실제 벡터 정합성을 구분해 표시."""
    # TODO D29-05-A-02: pending/ready/failed와 실제 벡터 정합성을 구분해 표시.
    # 힌트: index_status는 DB 인덱싱 상태이며 vector_fresh는 별도 검사 값입니다.
    raise NotImplementedError('D29-05-A-02: 직접 구현하세요')

def status_is_usable(raw: dict) -> bool:
    """ready 문자열 하나가 아닌 vector_fresh까지 확인합니다."""
    # TODO D29-05-A-03: ready 문자열 하나가 아닌 vector_fresh까지 확인합니다.
    # 힌트: index_status는 DB 인덱싱 상태이며 vector_fresh는 별도 검사 값입니다.
    raise NotImplementedError('D29-05-A-03: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from policy_05 import enforce_read_policy
