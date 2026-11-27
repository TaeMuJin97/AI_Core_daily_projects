"""B-05/I-03: 검색 질문과 원래 질문은 구별한다. 명시 ID는 정확히 제한."""
import re
from time import perf_counter
from app.rag.documents import to_document

from app.rag.ids import explicit_ids

class Retriever:
    def __init__(self, repo, embedder):
        self.repo=repo; self.embedder=embedder
    def search(self, query, category_code, top_k, meter, exact_ids=None):
        ids=sorted(explicit_ids(query) if exact_ids is None else exact_ids)
        vector=self.embedder.encode(query,meter)
        start=perf_counter()
        rows=[]
        # ID 지정 시 다른 보고서로 대체하지 않는다. 지정하지 않았다면 일반 의미 검색.
        for rid in ids or [None]:
            rows.extend(self.repo.candidates(vector,category_code,top_k,rid))
        meter.record('pgvector_retrieval',start)
        return [to_document(r) for r in sorted(rows,key=lambda r:(r['distance'],r['report_id']))[:top_k]]
