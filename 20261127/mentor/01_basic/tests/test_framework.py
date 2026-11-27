"""LangChain 설치 시에만 수행하는 실제 프레임워크 + Stub 검증. 유료 호출 없음."""
import pytest
pytest.importorskip('langchain')
pytest.importorskip('langchain_openai')
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.settings import Settings
from app.core.runtime import Runtime
from app.services.errors import ServiceError
from app.services.metrics import Meter
from app.schemas.agent import AskRequest
from app.rag.documents import to_document
from app.services.validator import check_tool_output
import json

class FakeToolModel(FakeMessagesListChatModel):
    # 실제 LangChain create_agent에 연결되는 테스트 모델. 외부 모델 성능 검증이 아니다.
    def bind_tools(self,tools,**kwargs):return self

class Repo:
    def lookup(self,rid):return {'status':'found','report_id':rid,'category_code':'RESEARCH_PLAN','index_status':'ready','revision':1,'embedding_fresh':True}
    def candidates(self,*args):return [{'report_id':63,'title':'fixture','content':'fixture 근거','overview':'fixture','category_code':'RESEARCH_PLAN','revision':1,'distance':0.1}]
    def preflight(self):return {'eligible_vectors':1,'db':'ready'}
class Emb:
    def encode(self,q,m):return [1.0]+[0.0]*383
class Rank:
    def rank(self,q,docs,m):return [d.model_copy(update={'metadata':{**d.metadata,'reranker_score':1.0}}) for d in docs]

def test_T04_document():
    d=to_document(Repo().candidates()[0]);assert d.page_content=='fixture 근거' and d.metadata['source_id']=='RPT-63'

def test_T07_framework_loop(monkeypatch):
    # 실제 Python Tool 2개가 create_agent에서 실행되고 ToolMessage와 ledger가 일치해야 한다.
    # 실제 create_agent를 사용하면서 Structured Output 전략과 스키마 전달도 확인한다.
    import app.agent as agent_module
    from langchain.agents.structured_output import ProviderStrategy
    from app.schemas.agent import ModelAnswer
    actual_create_agent=agent_module.create_agent
    def checked_create_agent(*args,**kwargs):
        strategy=kwargs['response_format']
        assert isinstance(strategy,ProviderStrategy) and strategy.schema is ModelAnswer
        return actual_create_agent(*args,**kwargs)
    monkeypatch.setattr(agent_module,'create_agent',checked_create_agent)
    calls=[{'id':'c1','name':'rag_search','args':{'query':'보고서 63 핵심 내용','k':1},'type':'tool_call'},
           {'id':'c2','name':'lookup_status','args':{'report_id':63},'type':'tool_call'}]
    final=json.dumps({'status':'completed','answer':'fixture [RPT-63]','source_ids':['RPT-63']})
    agent_model=FakeToolModel(responses=[AIMessage(content='',tool_calls=calls),AIMessage(content=final)])
    rag_model=FakeToolModel(responses=[AIMessage(content=final)])
    r=Runtime(Settings('','key','fake'),Repo(),Emb(),Rank(),lambda:agent_model)
    r.pipeline.model_factory=lambda:rag_model
    # Intermediate 이상의 optimizer는 이 고정 프레임워크 테스트에서만 끈다.
    r.pipeline.optimizer=None
    out=r.agent.ask('stub',AskRequest(question='보고서 63의 핵심 내용과 인덱싱 상태를 확인해 줘.'))
    assert out['status']=='completed' and len(out['tool_trace'])==2

class StubRuntime:
    settings=Settings('','','')
    def __init__(self):self.agent=self
    def health(self):return {'db':'ready','gpu':'fixture','llm':'configured'}
    def close(self):pass
    def ask(self,rid,req,meter):
        return {'request_id':rid,'status':'insufficient_evidence','answer':'fixture','sources':[],'tool_trace':[],
                'validation':{'citations_match_context':True,'required_tools_observed':False},'latency_ms':1.0}

def test_T08_api_stub():
    with TestClient(create_app(StubRuntime),raise_server_exceptions=False) as c:
        assert c.get('/health').status_code==200
        assert c.post('/api/v1/agent/ask',json={'question':'bad'}).status_code==422
        out=c.post('/api/v1/agent/ask',json={'question':'fixture question'});assert out.status_code==200
        assert out.json()['status']=='insufficient_evidence'

def test_T08_DB_error():
    class Broken(StubRuntime):
        def health(self):raise ServiceError('DB_UNAVAILABLE')
    with TestClient(create_app(Broken),raise_server_exceptions=False) as c:
        assert c.get('/health').json()['error']['code']=='DB_UNAVAILABLE'


def test_T06_direct_tool():
    from app.tools.db_tool import make_db_tool
    m=Meter(Settings('','',''))
    tool=make_db_tool(Repo(),'보고서 63 상태',m)
    msg=tool.invoke({'name':'lookup_status','args':{'report_id':63},'id':'direct-1','type':'tool_call'})
    assert json.loads(msg.content)['revision']==1 and 'direct-1' in m.ledger
    assert 'tool_call_id' not in tool.tool_call_schema.model_json_schema()['properties']


def test_T05_same_candidates_and_context():
    r=Runtime(Settings('','key','fake'),Repo(),Emb(),Rank(),lambda:None)
    r.pipeline.optimizer=None
    docs,info=r.pipeline.retrieve('보고서 63 핵심 내용','RESEARCH_PLAN',3,Meter(r.settings))
    assert [x['report_id'] for x in info['before']]==[x['report_id'] for x in info['after']]==[63]
    ctx,sources=r.pipeline.build_context(docs,1)
    assert json.loads(ctx)[0]['content']=='fixture 근거' and sources[0]['source_id']=='RPT-63'

def test_T06_invalid_tool_arg_schema():
    from app.tools.db_tool import make_db_tool
    m=Meter(Settings('','',''))
    tool=make_db_tool(Repo(),'보고서 63 상태',m)
    msg=tool.invoke({'name':'lookup_status','args':{'report_id':'63'},'id':'bad-id','type':'tool_call'})
    assert getattr(msg,'status',None)=='error' and not m.ledger


def test_T07_structured_response_contract(monkeypatch):
    """Agent state의 Pydantic 객체를 사용하며, 누락 시 실패한다. 공급자 호출은 하지 않는다."""
    from types import SimpleNamespace
    import app.agent as agent_module
    from app.schemas.agent import ModelAnswer
    from langchain.agents.structured_output import ProviderStrategy
    settings=Settings('','key','fake')
    request=AskRequest(question='근거 없는 문서를 설명해 줘.')
    # 실제 업무 Tool을 실행하지 않은 상태는 finalize에서 incomplete로 판단해야 한다.
    answer=ModelAnswer(status='insufficient_evidence',answer='근거 없음',source_ids=[])
    state={'messages':[AIMessage(content='JSON이 아닌 마지막 메시지')], 'structured_response':answer}
    def fake_create_agent(*args,**kwargs):
        assert isinstance(kwargs['response_format'],ProviderStrategy)
        return SimpleNamespace(invoke=lambda *a,**kw:state)
    monkeypatch.setattr(agent_module,'create_agent',fake_create_agent)
    svc=agent_module.AgentService(settings,Repo(),None,lambda:None)
    result=svc.ask('fixture',request)
    assert result['status']=='incomplete' and not result['tool_trace']
    state.pop('structured_response')
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR') as err:
        svc.ask('missing',request)
    assert err.value.reason=='invalid_structured_response'


@pytest.mark.parametrize('status,source_ids,answer,reason',[
    ('incomplete',['RPT-63'],'fixture [RPT-63]','rag_status_rule'),
    ('insufficient_evidence',['RPT-63'],'fixture [RPT-63]','rag_status_rule'),
    ('completed',[],'fixture','missing_rag_citation'),
])
def test_T04_rag_status_rule_preserved(status,source_ids,answer,reason):
    """Prompt를 개선했어도 부적절한 RAG 응답은 통과시키지 않는다."""
    message=AIMessage(content=json.dumps({'status':status,'answer':answer,'source_ids':source_ids}))
    model=FakeToolModel(responses=[message])
    r=Runtime(Settings('','key','fake'),Repo(),Emb(),Rank(),lambda:model)
    r.pipeline.optimizer=None
    with pytest.raises(ServiceError,match='OUTPUT_CONTRACT_ERROR') as err:
        r.pipeline.run('보고서 63 핵심 내용과 인덱싱 상태','보고서 63 핵심 내용',None,1,Meter(r.settings))
    assert err.value.reason==reason
