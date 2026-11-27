from time import perf_counter
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ToolCallLimitMiddleware, ModelCallLimitMiddleware
from langchain.agents.structured_output import ProviderStrategy
from langchain_openai import ChatOpenAI
from app.services.errors import ServiceError,llm_error
from app.services.metrics import Meter
from app.services.validator import trace_from_messages,finalize
from app.schemas.agent import StructuredModelAnswer
from app.tools.rag_tool import make_rag_tool
from app.tools.db_tool import make_db_tool

# TODO: Tool별 책임, 완료 상태와 출처 규칙, status_report_ids를 포함한 최종 스키마를 설계한다.
SYSTEM = """PROMPT_TEXT"""

def make_model(settings):
    pass

class AgentService:
    def __init__(self,settings,repo,pipeline,model_factory=None):
        self.settings=settings;self.repo=repo;self.pipeline=pipeline
        self.model_factory=model_factory or (lambda:make_model(settings))

    pass

# AgentService.ask 구현 시 ProviderStrategy(StructuredModelAnswer)를 사용하고
# result['structured_response']의 타입 및 실제 DB Tool 조회 ID를 검증한다.
# ToolMessage/ledger 대조 및 finalize 검증은 생략하지 않는다.
