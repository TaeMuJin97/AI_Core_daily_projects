"""A-01: 앱 구성의 조립 지점. 모델은 처음 사용 시에만 로드한다."""
from app.core.settings import load_settings,LEVEL
from app.db.connection import Database
from app.db.repository import Repository
from app.rag.embeddings import E5
from app.rag.retriever import Retriever
from app.rag.reranker import Reranker
from app.rag.pipeline import RagPipeline
from app.agent import AgentService,make_model
from app.core.preflight import preflight
from threading import Lock

class Runtime:
    def __init__(self,settings=None,repo=None,embedder=None,reranker=None,model_factory=None):
        self.settings=settings or load_settings()
        self.db=None if repo is not None else Database(self.settings)
        self.repo=repo if repo is not None else Repository(self.db)
        self.embedder=embedder if embedder is not None else E5(self.settings)
        self.reranker=reranker if reranker is not None else Reranker(self.settings)
        self.model_factory=model_factory or (lambda:make_model(self.settings))
        self.pipeline=RagPipeline(self.settings,Retriever(self.repo,self.embedder),self.reranker,self.model_factory)
        self.agent=AgentService(self.settings,self.repo,self.pipeline,self.model_factory)
    def health(self):
        return preflight(self.settings,self.repo)
    def close(self):
        if self.db:
            self.db.close()
