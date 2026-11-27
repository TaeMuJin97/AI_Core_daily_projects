"""TEST 013: 실제 RAG Tool 직접 검증 (유료). 실행: python -m test.013_test."""


def main():
    from test._support import paid_opt_in
    paid_opt_in()
    import json
    from test._support import report_ids
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.rag.embeddings import E5
    from app.rag.retriever import Retriever
    from app.rag.reranker import Reranker
    from app.rag.pipeline import RagPipeline
    from app.agent import make_model
    from app.tools.rag_tool import make_rag_tool
    from app.services.metrics import Meter
    s=load_settings(); db=Database(s); m=Meter(s)
    try:
        rid, _ = report_ids()
        q=f"보고서 {rid}의 핵심 내용"
        pipeline=RagPipeline(s,Retriever(Repository(db),E5(s)),Reranker(s),lambda:make_model(s))
        tool=make_rag_tool(pipeline,s,q,None,m)
        msg=tool.invoke({'name':'rag_search','args':{'query':q,'k':s.context_k},'id':'direct-rag-1','type':'tool_call'})
        result=json.loads(msg.content)
        print('tool:',msg.type,msg.tool_call_id,result)
        print('metrics:',m.summary())
        assert msg.tool_call_id in m.ledger
        assert result['status'] == 'found' and result['sources']
        assert {source['report_id'] for source in result['sources']} == {rid}
    finally:
        db.close()
    print("[PASS] TEST 013")


if __name__ == "__main__":
    main()
