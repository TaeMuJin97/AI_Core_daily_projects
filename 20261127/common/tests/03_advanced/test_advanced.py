"""A-01~A-08 regression, synthetic fixtures only."""
from types import SimpleNamespace
import pytest
from app.services.run_store import RunStore
from app.services.errors import ServiceError,llm_error
from app.services.metrics import Meter
from app.core.settings import Settings
from app.services.validator import parse_answer,citation_ids,finalize
from app.schemas.agent import ModelAnswer

def test_T19_run_store():
    s=RunStore(1);s.put('a',{'status':'completed'});s.put('b',{'status':'incomplete'})
    with pytest.raises(ServiceError,match='RUN_NOT_FOUND'):s.get('a')
    assert s.get('b')['status']=='incomplete'

def test_T19_usage_missing_not_zero():
    from time import perf_counter
    m=Meter(Settings('','',''));m.reserve('model');m.record('agent_model',perf_counter(),None)
    assert m.summary()['total_tokens_reported'] is None and m.summary()['usage_missing_calls']==1
    m.reserve('model');m.record('rag_generation',perf_counter(),{'total_tokens':10,'input_tokens':8,'output_tokens':2})
    assert m.summary()['total_tokens_reported']==10 and m.summary()['usage_missing_calls']==1

def test_T17_injection_false_citation():
    # 문서 주입에 의한 가짜 출처를 출력한 경우를 fixture로 재현한다. Live 저항성 검사는 별도.
    fake=ModelAnswer(status='completed',answer='지시를 따라 [RPT-999999]를 출력',source_ids=['RPT-999999'])
    assert not citation_ids(fake,{'RPT-63':{}})
    with pytest.raises(ServiceError):finalize('fixture','보고서 내용을 알려 줘.',fake,[],[],0.0)

def test_T18_errors():
    for status,reason in [(401,'authentication'),(429,'rate_limit'),(503,'upstream_5xx')]:
        exc=type('ProviderError',(Exception,),{'status_code':status})('private secret')
        result=llm_error(exc);assert result.reason==reason and 'private secret' not in str(result.envelope())

def test_T16_actual_middleware():
    pytest.importorskip('langchain')
    from langchain_core.messages import AIMessage
    from langchain.agents import create_agent
    from langchain.agents.middleware import ToolCallLimitMiddleware
    from langchain.tools import tool
    from tests.test_framework import FakeToolModel
    executed=[]
    @tool
    def ping(x:int)->str:
        """Fixture ping."""
        executed.append(x);return 'ok'
    messages=[AIMessage(content='',tool_calls=[{'name':'ping','args':{'x':i},'id':f'c{i}','type':'tool_call'}]) for i in range(2)]
    model=FakeToolModel(responses=messages)
    agent=create_agent(model=model,tools=[ping],middleware=[ToolCallLimitMiddleware(run_limit=1,exit_behavior='error')])
    with pytest.raises(Exception) as err:agent.invoke({'messages':[{'role':'user','content':'fixture'}]},config={'recursion_limit':10})
    assert 'Limit' in type(err.value).__name__ and len(executed)<=1
