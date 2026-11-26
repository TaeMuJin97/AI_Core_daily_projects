"""03 · @tool·Pydantic·JSON Schema · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from langchain.tools import tool
from pydantic import BaseModel, Field


class ReportStatusArgs(BaseModel):
    """lookup_status Tool의 입력 Schema 계약 (reports.report_id 양의 정수 전용)."""

    report_id: int = Field(
        ge=1,
        strict=True,
        description="인덱싱 상태를 조회할 보고서의 양의 정수 ID (reports.report_id)",
    )


def validate_id(report_id: int) -> int:
    """실제 reports.report_id인 양의 정수만 허용합니다."""
    # TODO D29-03-B-01
    # [흐름 이해: DB 조회 전에 잘못된 report_id를 애플리케이션 경계에서 즉시 차단]
    # 1) Python에서 bool은 int의 하위 클래스이므로 isinstance(report_id, bool)을 먼저 제외합니다.
    # 2) 순수 int가 아니거나 1 미만(0, 음수)이면 ValueError를 발생시켜 SQL 실행을 막습니다.
    if isinstance(report_id, bool) or not isinstance(report_id, int):
        raise ValueError("report_id는 bool이 아닌 정수(int)여야 합니다.")
    if report_id < 1:
        raise ValueError("report_id는 1 이상의 양의 정수여야 합니다.")
    return report_id


def register_status_tool():
    """@tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다."""
    # TODO D29-03-B-02
    # [흐름 이해: Pydantic args_schema + 명확한 Docstring으로 LangChain Tool 등록]
    # 1) args_schema=ReportStatusArgs를 지정해 registered.args_schema.model_json_schema()가
    #    JSON Schema(type=integer, minimum=1, required=['report_id'])를 노출하도록 합니다.
    # 2) Docstring은 LLM이 "언제 이 도구를 선택해야 하는지" 판단하는 핵심 기준입니다.
    # 3) 실제 DB 조회(coursekit.db.fetch_report_status)는 Tool이 invoke()될 때만 실행합니다.
    @tool("lookup_status", args_schema=ReportStatusArgs)
    def lookup_status(report_id: int) -> dict:
        """기존 report_agent_lab PostgreSQL에서 특정 report_id의 보고서 인덱싱 상태(index_status, revision, vector_fresh)를 읽기 전용으로 조회합니다."""
        valid_id = validate_id(report_id)
        from coursekit.db import fetch_report_status

        return fetch_report_status(valid_id)

    return lookup_status