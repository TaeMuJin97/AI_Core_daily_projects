"""B-09: 모델이 호출 요청을 생성하더라도 Python은 별도로 입력을 검증한다."""
import json
from langchain.tools import tool
from langchain_core.tools import InjectedToolCallId
from typing import Annotated
from pydantic import BaseModel, ConfigDict, ValidationError
from app.schemas.agent import Query, Category, K
from app.services.validator import check_tool_output
from app.services.errors import ServiceError
from app.rag.retriever import explicit_ids

class RagInput(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    query: Query
    category_code: Category | None=None
    k: K=3

def make_rag_tool(pipeline,settings,question,category,meter):
    @tool
    def rag_search(query: Query, tool_call_id: Annotated[str,InjectedToolCallId], category_code: Category | None=None, k: K=3) -> str:
        """보고서의 기술적 내용, 근거, 요약을 실제 검색한다. query 1~300자, category_code는 6개 코드 또는 null, k는 1~5. 지정 보고서 번호를 보존한다. 상태 조회는 별도 도구다."""
        meter.reserve('tool')
        try:
            args=RagInput.model_validate({'query':query,'category_code':category_code,'k':k})
            if args.k>settings.retrieve_k or (category is not None and args.category_code not in (None,category)):
                raise ValueError()
            effective_category=category if category is not None else args.category_code
            original_ids=explicit_ids(question)
            query_ids=explicit_ids(args.query)
            if original_ids and not query_ids<=original_ids:
                raise ValueError()
            # 원 질문에서 특정 ID가 있었는데 검색 인수에서 빠졌다면 안전하게 유지한다.
            query=args.query
            if original_ids and not query_ids:
                query=' '.join(f'RPT-{i}' for i in sorted(original_ids))+' '+query
                if len(query)>300:
                    raise ValueError()
            # BEGIN B-09
            result=pipeline.run(question,query,effective_category,args.k,meter)
            result=check_tool_output('rag_search',result)
            # END B-09
        except (ValidationError,ValueError):
            result={'status':'error','query':'invalid_input','answer':'invalid_input','sources':[]}
        except ServiceError as exc:
            meter.fatal=exc
            raise
        meter.save_tool(tool_call_id,'rag_search',result,{'category_code':category,'k':k})
        return json.dumps(result,ensure_ascii=False)
    rag_search.handle_validation_error="invalid_input"
    return rag_search
