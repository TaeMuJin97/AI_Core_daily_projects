"""B-12: API 요청/응답 계약. 사용자가 서버 설정을 변경할 수 없다."""
from typing import Literal, Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, StrictInt
Category = Literal['EXPERIMENT','DAILY_WORK','RESEARCH_PLAN','DATA_PROCESSING','PROMPT','MEETING']
Status = Literal['completed','insufficient_evidence','incomplete']
Question = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=5,max_length=1000)]
Query = Annotated[str, StringConstraints(strict=True, strip_whitespace=True,min_length=1,max_length=300)]
ReportId = Annotated[StrictInt, Field(ge=1,le=9223372036854775807)]
K = Annotated[StrictInt, Field(ge=1,le=5)]
class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
class AskRequest(Contract):
    question: Question
    category_code: Category | None = None
class DebugRequest(Contract):
    query: Query
    category_code: Category | None = None
    top_k: Annotated[StrictInt, Field(ge=1,le=30)] = 8
class Source(Contract):
    source_id: str
    report_id: ReportId
    title: str
    category_code: Category
    revision: Annotated[StrictInt, Field(ge=1)]
class Trace(Contract):
    tool_call_id: str
    tool: Literal['rag_search','lookup_status']
    status: Literal['found','not_found','error']
class Validation(Contract):
    citations_match_context: bool
    required_tools_observed: bool
class AskResponse(Contract):
    request_id: str
    status: Status
    answer: str
    sources: list[Source]
    tool_trace: list[Trace]
    validation: Validation
    latency_ms: float
class StatusResult(Contract):
    status: Literal['found','not_found','error']
    report_id: ReportId
    category_code: Category | None = None
    index_status: Literal['pending','ready','failed'] | None = None
    revision: Annotated[StrictInt,Field(ge=1)] | None = None
    embedding_fresh: bool | None = None
class RagResult(Contract):
    status: Literal['found','not_found','error']
    query: Query
    answer: str
    sources: list[Source]
class ModelAnswer(Contract):
    status: Status
    answer: Annotated[str,StringConstraints(strip_whitespace=True,min_length=1,max_length=12000)]
    source_ids: list[str]

class StructuredModelAnswer(ModelAnswer):
    # I-06: model must name the IDs of actual DB status results it relies on; server validates them.
    status_report_ids:list[ReportId]
