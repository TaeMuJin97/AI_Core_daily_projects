"""FastAPI 실제 HTTP(TestClient) + stub 의존성. 유료/DB/CUDA 실측 아님."""
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.settings import Settings
from app.services.errors import ServiceError
import pytest
class StubRuntime:
    settings=Settings('','','')
    def __init__(self):self.agent=self
    def health(self):return {'db':'ready','gpu':'fixture','llm':'configured'}
    def close(self):pass
    def ask(self,rid,req,meter):
        return {'request_id':rid,'status':'insufficient_evidence','answer':'fixture','sources':[],'tool_trace':[],
                'validation':{'citations_match_context':True,'required_tools_observed':False},'latency_ms':1.0}
def test_T08_http_contract():
    with TestClient(create_app(StubRuntime),raise_server_exceptions=False) as c:
        assert c.get('/health').status_code==200
        response=c.post('/api/v1/agent/ask',json={'question':'fixture question'})
        assert response.status_code==200 and response.json()['status']=='insufficient_evidence'
        assert '/api/v1/agent/ask' in c.get('/openapi.json').json()['paths']
@pytest.mark.parametrize('body',[{'question':'bad'},{'question':'fixture valid','category_code':'bad'},{'question':'fixture valid','max_tool_calls':1}])
def test_T08_422(body):
    with TestClient(create_app(StubRuntime),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/agent/ask',json=body)
        assert r.status_code==422 and r.json()['error']['code']=='VALIDATION_ERROR'
@pytest.mark.parametrize('code,http',[('DB_UNAVAILABLE',503),('GPU_UNAVAILABLE',503),('LLM_UNAVAILABLE',503),('LLM_TIMEOUT',504),('TOOL_CONTRACT_ERROR',500)])
def test_T10_failure_envelope(code,http):
    class Broken(StubRuntime):
        def ask(self,*args):raise ServiceError(code)
    with TestClient(create_app(Broken),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/agent/ask',json={'question':'fixture valid'})
        assert r.status_code==http and r.json()['error']['code']==code


def test_T19_run_endpoint():
    from app.services.run_store import RunStore
    class AdvancedStub(StubRuntime):
        def __init__(self):super().__init__();self.runs=RunStore()
    with TestClient(create_app(AdvancedStub),raise_server_exceptions=False) as c:
        r=c.post('/api/v1/agent/ask',json={'question':'fixture valid'})
        assert r.status_code==200
        rid=r.json()['request_id'];assert r.headers['X-Request-ID']==rid
        run=c.get('/api/v1/agent/runs/'+rid).json();assert run['request_id']==rid and 'answer' not in run and 'question' not in run
        assert c.get('/api/v1/agent/runs/missing').status_code==404
