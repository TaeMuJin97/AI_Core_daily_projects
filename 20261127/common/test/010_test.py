"""TEST 010: Context·Prompt 구성 검증 (LLM 미호출). 실행: python -m test.010_test."""


def main():
    import json
    from test._support import report_ids
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.rag.embeddings import E5
    from app.rag.retriever import Retriever
    from app.rag.reranker import Reranker
    from app.rag.pipeline import RagPipeline,RAG_PROMPT
    from app.services.metrics import Meter
    s=load_settings(); db=Database(s); m=Meter(s)
    try:
        rid, _ = report_ids()
        q=f"보고서 {rid}의 핵심 내용"
        # 이 단계에서는 실제 LLM 호출을 하지 않는다. model_factory는 아직 연결하지 않음.
        rag=RagPipeline(s,Retriever(Repository(db),E5(s)),Reranker(s),lambda:None)
        docs,info=rag.retrieve(q,None,s.retrieve_k,m)
        context,sources=rag.build_context(docs,s.context_k)
        assert sources and {x['source_id'] for x in json.loads(context)}=={x['source_id'] for x in sources}
        messages=RAG_PROMPT.format_messages(question=q,query=q,context=context)
        print('messages:',[x.type for x in messages]); print('context chars:',len(context))
        print('sources:',sources)
        assert len(context) <= s.context_chars
        assert m.model_calls == 0
    finally:
        db.close()
    print("[PASS] TEST 010")


if __name__ == "__main__":
    main()
