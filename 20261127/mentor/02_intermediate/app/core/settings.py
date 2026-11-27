"""B-01/B-02: 환경변수는 서버에서만 읽는다. 실제 키는 출력하지 않는다."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from app.services.errors import ServiceError

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'intfloat/multilingual-e5-small'
RERANKER = 'BAAI/bge-reranker-v2-m3'
LEVEL = 'intermediate'

@dataclass(frozen=True)
class Settings:
    database_url: str = field(repr=False)
    api_key: str = field(repr=False)
    llm_model: str
    embedding_model: str = MODEL
    reranker_model: str = RERANKER
    retrieve_k: int = 8
    context_k: int = 3
    max_tool_calls: int = 4
    max_model_calls: int = 14
    llm_timeout_seconds: float = 30
    context_chars: int = 9000
    rerank_batch_size: int = 2
    rerank_max_length: int = 512
    db_timeout_ms: int = 10000
    @property
    def llm_configured(self):
        return bool(self.api_key and self.llm_model)

    def validate(self):
        try:
            url = make_url(self.database_url)
            if url.drivername != 'postgresql+psycopg' or url.database != 'report_agent_lab':
                raise ValueError()
        except Exception:
            raise ServiceError('DB_UNAVAILABLE') from None
        if (self.embedding_model != MODEL or self.reranker_model != RERANKER
            or not 1 <= self.context_k <= min(5, self.retrieve_k) or not 1 <= self.retrieve_k <= 30
            or not 1 <= self.max_tool_calls <= 12 or not 2 <= self.max_model_calls <= 40
            or not 1 <= self.llm_timeout_seconds <= 120 or not 1000 <= self.context_chars <= 20000
            or not 1 <= self.rerank_batch_size <= 16 or not 128 <= self.rerank_max_length <= 1024
            or not 1000 <= self.db_timeout_ms <= 60000):
            raise ServiceError('CONFIG_INVALID')
        return self


def load_settings():
    load_dotenv(ROOT / '.env', override=False)
    os.environ['LANGSMITH_TRACING']='false'
    os.environ['LANGCHAIN_TRACING_V2']='false'
    try:
        return Settings(os.getenv('DATABASE_URL',''), os.getenv('OPENAI_API_KEY','').strip(),
            os.getenv('LLM_MODEL','').strip(), os.getenv('EMBEDDING_MODEL',MODEL),
            os.getenv('RERANKER_MODEL',RERANKER), int(os.getenv('RETRIEVE_K','8')),
            int(os.getenv('CONTEXT_K','3')), int(os.getenv('MAX_TOOL_CALLS','4')),
            int(os.getenv('MAX_MODEL_CALLS','14')), float(os.getenv('LLM_TIMEOUT_SECONDS','30')),
            int(os.getenv('CONTEXT_CHARS','9000')), int(os.getenv('RERANK_BATCH_SIZE','2')),
            int(os.getenv('RERANK_MAX_LENGTH','512')), int(os.getenv('DB_TIMEOUT_MS','10000'))).validate()
    except (ValueError, TypeError):
        raise ServiceError('CONFIG_INVALID') from None
