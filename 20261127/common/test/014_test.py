"""TEST 014: 실제 Agent 복합 질문 검증 (유료). 실행: python -m test.014_test."""


def main():
    from test._support import paid_opt_in
    paid_opt_in()
    import json
    from test._support import report_ids, check_completed
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.rag.embeddings import E5
    from app.rag.retriever import Retriever
    from app.rag.reranker import Reranker
    from app.rag.pipeline import RagPipeline
    from app.agent import AgentService,make_model
    from app.schemas.agent import AskRequest
    from app.services.metrics import Meter
    s=load_settings(); db=Database(s); m=Meter(s)
    try:
        repo=Repository(db); factory=lambda:make_model(s)
        pipeline=RagPipeline(s,Retriever(repo,E5(s)),Reranker(s),factory)
        agent=AgentService(s,repo,pipeline,factory)
        rid, _ = report_ids()
        body=AskRequest(question=f'보고서 {rid}의 핵심 내용과 인덱싱 상태를 함께 설명해 줘.')
        result=agent.ask('manual-demo',body,m)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        print('실제 ledger:',[(k,v['name'],v['result']['status']) for k,v in m.ledger.items()])
        check_completed(result, {'rag_search', 'lookup_status'})
        assert {source['report_id'] for source in result['sources']} == {rid}
    finally:
        db.close()
    print("[PASS] TEST 014")


if __name__ == "__main__":
    main()
