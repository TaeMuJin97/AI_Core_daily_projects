"""TEST 009: Cross-Encoder 동일 후보 재정렬 검증. 실행: python -m test.009_test."""


def main():
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.rag.embeddings import E5
    from app.rag.retriever import Retriever
    from app.rag.reranker import Reranker
    from app.services.metrics import Meter
    s=load_settings(); db=Database(s); m=Meter(s)
    try:
        q='RAG 근거 인용 정확도 향상'
        before=Retriever(Repository(db),E5(s)).search(q,None,s.retrieve_k,m)
        assert before
        reranker=Reranker(s); after=reranker.rank(q,before,m)
        a=[d.metadata['report_id'] for d in before]
        b=[d.metadata['report_id'] for d in after]
        assert sorted(a)==sorted(b)
        assert str(reranker.model.model.device) == 'cuda:0'
        scores = [d.metadata['reranker_score'] for d in after]
        assert scores == sorted(scores, reverse=True)
        print('device:',reranker.model.model.device)
        print('before:',[(d.metadata['report_id'],d.metadata['distance']) for d in before])
        print('after:',[(d.metadata['report_id'],d.metadata['reranker_score']) for d in after])
        print(m.summary())
    finally:
        db.close()
    print("[PASS] TEST 009")


if __name__ == "__main__":
    main()
