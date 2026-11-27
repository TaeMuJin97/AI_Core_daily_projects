"""TEST 008: 실제 pgvector 검색 및 명시 ID·원문 검증. 실행: python -m test.008_test."""


def main():
    from test._support import report_ids
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.rag.embeddings import E5
    from app.rag.retriever import Retriever
    from app.rag.documents import source_of
    from app.services.metrics import Meter
    s=load_settings(); db=Database(s); meter=Meter(s)
    try:
        ret=Retriever(Repository(db),E5(s))
        docs=ret.search('RAG 근거 인용 정확도 향상',None,s.retrieve_k,meter)
        assert 0 < len(docs) <= s.retrieve_k
        distances = [d.metadata['distance'] for d in docs]
        assert distances == sorted(distances)
        for d in docs:
            print(source_of(d),'distance=',d.metadata['distance'])
        rid, _ = report_ids()
        exact=ret.search(f'보고서 {rid} 핵심 내용',None,s.retrieve_k,meter)
        assert [d.metadata['report_id'] for d in exact]==[rid]
        print('exact:',source_of(exact[0]))
        assert exact[0].metadata['source_id'] == f'RPT-{rid}' and exact[0].page_content
        print('원문 미리보기(로컬 확인):',exact[0].page_content[:200])
    finally:
        db.close()
    print("[PASS] TEST 008")


if __name__ == "__main__":
    main()
