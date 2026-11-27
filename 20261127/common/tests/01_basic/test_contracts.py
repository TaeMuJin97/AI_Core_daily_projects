"""고정 Fixture: 실제 DB/GPU/LLM 성공 증거가 아니다. pytest -q."""
import json
from types import SimpleNamespace as Msg
import pytest
from pydantic import ValidationError
from app.schemas.agent import AskRequest,ModelAnswer,ReportId,StatusResult
from app.services.validator import parse_answer,citation_ids,check_tool_output,trace_from_messages,finalize
from app.services.errors import ServiceError,llm_error
from app.services.metrics import Meter
from app.rag.ids import explicit_ids
from app.core.settings import Settings

SOURCE={'source_id':'RPT-63','report_id':63,'title':'fixture title','category_code':'RESEARCH_PLAN','revision':1}
RAG={'status':'found','query':'fixture query','answer':'근거 [RPT-63]','sources':[SOURCE]}
STATUS={'status':'found','report_id':63,'category_code':'RESEARCH_PLAN','index_status':'ready','revision':1,'embedding_fresh':True}
QUESTION='보고서 63의 핵심 내용과 인덱싱 상태를 확인해 줘.'
ANSWER=ModelAnswer(status='completed',answer='핵심 내용 [RPT-63]',source_ids=['RPT-63'])
def entry(name,result,args=None):
    return {'name':name,'result':result,'args':args or {}}

@pytest.mark.parametrize('body',[{'question':'  '},{'question':1},{'question':'유효한 질문입니다','category_code':'OTHER'}, {'question':'유효한 질문입니다','max_tool_calls':99}])
def test_T08_bad_request(body):
    with pytest.raises(ValidationError):AskRequest.model_validate(body)

def test_T08_valid_request():
    assert AskRequest(question='  보고서 내용을 설명해 주세요. ').question=='보고서 내용을 설명해 주세요.'

@pytest.mark.parametrize('rid',[0,-1,'63',True])
def test_T06_wrong_report_id(rid):
    with pytest.raises(ValidationError):StatusResult(status='not_found',report_id=rid)

def test_T06_wrong_output():
    with pytest.raises(ServiceError):check_tool_output('lookup_status',{'status':'found','report_id':63})
    with pytest.raises(ServiceError):check_tool_output('rag_search',{**RAG,'sources':[]})
    assert check_tool_output('lookup_status',{'status':'not_found','report_id':63})['status']=='not_found'

def test_T09_bad_citations():
    assert citation_ids(ANSWER,{'RPT-63':SOURCE})
    bad=ModelAnswer(status='completed',answer='허위 [RPT-999999]',source_ids=['RPT-999999'])
    assert not citation_ids(bad,{'RPT-63':SOURCE})
    with pytest.raises(ServiceError):finalize('x',QUESTION,bad,[],[entry('rag_search',RAG)],1.0)

def test_T09_incomplete_and_complete():
    assert finalize('x',QUESTION,ModelAnswer(status='completed',answer='임의 답변',source_ids=[]),[],[],1.0)['status']=='incomplete'
    assert finalize('x',QUESTION,ANSWER,[],[entry('rag_search',RAG)],1.0)['status']=='incomplete'
    done=finalize('x',QUESTION,ANSWER,[],[entry('rag_search',RAG),entry('lookup_status',STATUS)],1.0)
    assert done['status']=='completed' and 'revision=1' in done['answer']
    status_only=finalize('x','보고서 63의 현재 인덱싱 상태',ModelAnswer(status='completed',answer='상태 확인',source_ids=[]),[],[entry('lookup_status',STATUS)],1.0)
    assert status_only['status']=='completed' and not status_only['sources']

def test_T07_actual_message_pairing():
    messages=[Msg(type='ai',tool_calls=[{'id':'a','name':'rag_search'}]),Msg(type='tool',tool_call_id='a',name='rag_search',content=json.dumps(RAG))]
    ledger={'a':entry('rag_search',RAG)}
    traces,observed=trace_from_messages(messages,ledger)
    assert traces==[{'tool_call_id':'a','tool':'rag_search','status':'found'}]
    with pytest.raises(ServiceError):trace_from_messages(messages,{})
    with pytest.raises(ServiceError):trace_from_messages(messages,{'a':entry('rag_search',{**RAG,'answer':'changed'})})
    with pytest.raises(ServiceError):trace_from_messages(messages[:1],ledger)

def test_T10_no_answer():
    answer=ModelAnswer(status='insufficient_evidence',answer='정보 부족',source_ids=[])
    out=finalize('x','화성 낙타 미용실 운영 시간',answer,[],[entry('rag_search',{'status':'not_found','query':'x','answer':'없음','sources':[]})],1.0)
    assert out['status']=='insufficient_evidence' and not out['sources']

def test_T10_limits_and_errors():
    meter=Meter(Settings('','', '',max_tool_calls=1,max_model_calls=2))
    meter.reserve('tool')
    with pytest.raises(ServiceError,match='EXECUTION_LIMIT'):meter.reserve('tool')
    class FakeRateLimit(Exception):status_code=429
    e=llm_error(FakeRateLimit('secret-value'))
    assert e.http_status==503 and 'secret-value' not in str(e.envelope())
    assert llm_error(TimeoutError()).http_status==504

def test_T13_format():
    with pytest.raises(ServiceError):parse_answer('not json')
    with pytest.raises(ServiceError):parse_answer('{"status":"completed","answer":"x","source_ids":[],"fake":true}')

def test_exact_ids():
    assert explicit_ids('보고서 63과 RPT-131 비교')=={63,131}


def test_T09_category_and_wrong_id_scope():
    with pytest.raises(ServiceError,match='TOOL_CONTRACT_ERROR'):
        finalize('x',QUESTION,ANSWER,[],[entry('rag_search',RAG)],1.0,'EXPERIMENT')
    with pytest.raises(ServiceError,match='TOOL_CONTRACT_ERROR'):
        finalize('x','보고서 64의 핵심 내용',ANSWER,[],[entry('rag_search',RAG)],1.0)

def test_T09_lookup_argument_mismatch():
    messages=[Msg(type='ai',tool_calls=[{'id':'b','name':'lookup_status','args':{'report_id':64}}]),Msg(type='tool',tool_call_id='b',name='lookup_status',content=json.dumps(STATUS))]
    with pytest.raises(ServiceError):trace_from_messages(messages,{'b':entry('lookup_status',STATUS)})
