"""03 · @tool·Pydantic·JSON Schema · 응용 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def validate_id(report_id: int) -> int:
    """실제 reports.report_id인 양의 정수만 허용합니다."""
    # 해설 D29-03-I-01: 모델에게 노출될 인수 Schema와 실제 Python Tool의 실행을 별도 관찰합니다.
    # 검수 기준: report_id는 실제 DB의 양의 정수이며 task_id가 아닙니다.
    from coursekit.contracts import report_id_from
    return report_id_from(report_id)

def register_status_tool():
    """@tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다."""
    # 해설 D29-03-I-02: 모델에게 노출될 인수 Schema와 실제 Python Tool의 실행을 별도 관찰합니다.
    # 검수 기준: report_id는 실제 DB의 양의 정수이며 task_id가 아닙니다.
    from langchain.tools import tool
    import json
    from coursekit.db import fetch_report_status
    @tool('lookup_status')
    def lookup_status(report_id:int)->str:
        """기존 보고서 report_id의 인덱싱 상태를 읽기 전용 조회합니다. task_id가 아닙니다."""
        return json.dumps(fetch_report_status(validate_id(report_id)),ensure_ascii=False,default=str)
    return lookup_status


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_03 import schema_fields
