"""I-05: Pydantic args_schema 명시. tool_call_id는 서버가 주입하는 필드."""
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from app.schemas.agent import Contract,Query,Category,K,ReportId
class RagToolArgs(Contract):
    query:Query
    category_code:Category|None=None
    k:K=3
    tool_call_id:Annotated[str,InjectedToolCallId]
class StatusToolArgs(Contract):
    report_id:ReportId
    tool_call_id:Annotated[str,InjectedToolCallId]
