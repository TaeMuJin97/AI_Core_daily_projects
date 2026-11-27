"""B-10: report_id만 받으며 임의 SQL은 받지 않는다."""
import json
from langchain.tools import tool
from langchain_core.tools import InjectedToolCallId
from typing import Annotated
from pydantic import BaseModel,ConfigDict,ValidationError
from app.schemas.agent import ReportId
from app.services.validator import check_tool_output
from app.services.errors import ServiceError
from app.rag.retriever import explicit_ids

class LookupInput(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    report_id: ReportId

def make_db_tool(repo,question,meter):
    @tool
    def lookup_status(report_id: ReportId, tool_call_id: Annotated[str,InjectedToolCallId]) -> str:
        """보고서 번호(양의 정수)의 현재 index_status, revision, embedding_fresh를 읽기 전용 조회한다. 문서 요약에는 사용하지 않는다."""
        meter.reserve('tool')
        try:
            args=LookupInput.model_validate({'report_id':report_id})
            ids=explicit_ids(question)
            if ids and args.report_id not in ids:
                raise ValueError()
            result=check_tool_output('lookup_status',repo.lookup(args.report_id))
            if result['report_id']!=args.report_id:
                raise ServiceError('TOOL_CONTRACT_ERROR','wrong_report_id')
        except (ValidationError,ValueError):
            # Tool 입력 오류는 정상 조회로 기록하지 않고 ToolMessage error로 전달.
            from langchain_core.tools import ToolException
            raise ToolException('invalid_input') from None
        except ServiceError as exc:
            meter.fatal=exc
            raise
        meter.save_tool(tool_call_id,'lookup_status',result,{'report_id':args.report_id})
        return json.dumps(result,ensure_ascii=False)
    lookup_status.handle_tool_error=True
    lookup_status.handle_validation_error='invalid_input'
    return lookup_status
