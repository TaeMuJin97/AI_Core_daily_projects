"""I-01/I-02: LLM Rewrite/Multi-query. 원 질문은 절대 삭제하지 않는다."""
import json,re
from time import perf_counter
from pydantic import BaseModel,ConfigDict,Field,ValidationError
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.agent import Query
from app.rag.ids import explicit_ids
from app.services.errors import ServiceError,llm_error

class SearchQueries(BaseModel):
    model_config=ConfigDict(strict=True,extra='forbid')
    queries:list[Query]=Field(min_length=1,max_length=2)

PROMPT=ChatPromptTemplate.from_messages([('system','보고서 의미 검색을 위해 원 질문의 의도와 고유명사, 수치, 보고서 번호를 보존하여 검색 질문 1~2개를 생성한다. '
    '새 사실/정답/ID를 추가하지 마라. JSON 객체 queries(문자열 목록)만 반환.'),('human','원래 검색 질문: {query}')])

def preserve_queries(original,alternatives):
    # 명시 ID 및 영문 기술 용어/수치 보존의 최소 기계적 검사. 의미 보존은 사람 평가 필요.
    anchors=set(re.findall(r'[A-Za-z][A-Za-z0-9_-]*|[0-9]+(?:\.[0-9]+)?',original.lower()))
    out=[original]
    for q in alternatives:
        if q not in out and explicit_ids(q)==explicit_ids(original) and anchors<=set(re.findall(r'[A-Za-z][A-Za-z0-9_-]*|[0-9]+(?:\.[0-9]+)?',q.lower())):
            out.append(q)
    return out[:3]

class QueryOptimizer:
    def __init__(self,model_factory):self.model_factory=model_factory
    def queries(self,query,meter):
        try:
            meter.reserve('model');start=perf_counter()
            msg=(PROMPT|self.model_factory()).invoke({'query':query})
            meter.record('query_rewrite',start,getattr(msg,'usage_metadata',None))
        except Exception as exc:raise llm_error(exc) from None
        try:
            obj=SearchQueries.model_validate_json(msg.content)
        except (ValidationError,TypeError):
            raise ServiceError('OUTPUT_CONTRACT_ERROR','rewrite_json') from None
        return preserve_queries(query,obj.queries)
