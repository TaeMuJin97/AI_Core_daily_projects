"""05 · PostgreSQL Read-only lookup_status · 응용 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def parse_report_id(value) -> int:
    """task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다."""
    # 해설 D29-05-I-01: 보고서 상태는 pending/ready/failed이고 제출 여부가 아닙니다.
    # 검수 기준: ready 문자열뿐 아니라 Model·Revision·Overview Hash가 일치하는지 검증합니다.
    from coursekit.contracts import report_id_from
    return report_id_from(value)

def status_view(raw: dict) -> dict:
    """pending/ready/failed와 실제 벡터 정합성을 구분해 표시."""
    # 해설 D29-05-I-02: 보고서 상태는 pending/ready/failed이고 제출 여부가 아닙니다.
    # 검수 기준: ready 문자열뿐 아니라 Model·Revision·Overview Hash가 일치하는지 검증합니다.
    if raw['status']!='ok':return {'status':'not_found','report_id':raw['report_id']}
    return {'report_id':raw['report_id'],'index_status':raw['index_status'],
            'revision':raw['revision'],'vector_fresh':raw['vector_fresh']}


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_05 import status_is_usable
