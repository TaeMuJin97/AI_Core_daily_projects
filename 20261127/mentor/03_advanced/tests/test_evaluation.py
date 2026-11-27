import pytest
from app.evaluation.retrieval_eval import scores
from app.evaluation.debug_report import diagnose

def test_T14_scores():
    assert scores([7,63,131],{'63':2,'131':1},2)['recall']==0.5
    assert 0<scores([7,63,131],{'63':2,'131':1},2)['ndcg']<1
    assert scores([63,63,131],{'63':2,'131':1},2)=={'recall':1.0,'mrr':1.0,'ndcg':1.0}
    assert scores([131,63],{'63':2,'131':1},2)['ndcg']<1
    assert scores([63],{},3)=={'recall':None,'mrr':None,'ndcg':None}

def test_T14_diagnose():
    assert diagnose({'state':'dataset_changed'})=='Gold snapshot 변경'
    assert 'Retrieval miss' in diagnose({'state':'observed','before':{'recall':0},'after':{'recall':0}})

def test_T11_preserve():
    pytest.importorskip('langchain_core')
    from app.rag.query_optimizer import preserve_queries
    original='보고서 63 RAG 근거'
    assert preserve_queries(original,['보고서 64 RAG 근거','RAG 근거 비교 보고서 63'])==[original,'RAG 근거 비교 보고서 63']


def test_T13_explicit_args_schema():
    pytest.importorskip('langchain_core')
    from app.schemas.tools import RagToolArgs,StatusToolArgs
    from pydantic import ValidationError
    for payload in [{'query':'RAG','category_code':'BAD','tool_call_id':'a'},{'query':'RAG','k':6,'tool_call_id':'a'},{'query':'RAG','k':'3','tool_call_id':'a'}]:
        with pytest.raises(ValidationError):RagToolArgs.model_validate(payload)
    with pytest.raises(ValidationError):StatusToolArgs.model_validate({'report_id':'63','tool_call_id':'a'})

def test_T11_dedup_same_metadata():
    pytest.importorskip('langchain_core')
    from app.rag.pipeline import RagPipeline
    from app.rag.documents import to_document
    from app.core.settings import Settings
    from app.services.metrics import Meter
    class Ret:
        def search(self,q,c,k,m,ids):
            assert c=='RESEARCH_PLAN'
            return [to_document({'report_id':63,'title':'fixture','content':'fixture','overview':'fixture','category_code':c,'revision':1,'distance':0.1})]
    class Rank:
        def rank(self,q,docs,m):return [d.model_copy(update={'metadata':{**d.metadata,'reranker_score':0.7}}) for d in docs]
    class Opt:
        def queries(self,q,m):return [q,'expanded']
    settings=Settings('','','');p=RagPipeline(settings,Ret(),Rank(),lambda:None,Opt())
    docs,info=p.retrieve('RAG 근거 인용','RESEARCH_PLAN',8,Meter(settings))
    assert len(docs)==1 and docs[0].metadata['source_id']=='RPT-63'
    assert info['candidate_count_raw']==2 and info['candidate_count_after_dedup']==1
