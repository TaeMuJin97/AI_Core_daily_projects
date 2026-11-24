# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `04_candidate_retrieval` (Candidate Retrieval 후보 계약 확인)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **live** (`execution_mode: "live_e5_cuda_postgresql"`, `outputs/day27_04_live.json` 실측 완료 및 `outputs/day27_04_fixture.json` 사전 검증 완료)
- 요청 질문과 Category: `Q01` (`category: "시설"`) — `candidate_k: 5`, `context_k: 2`
- Query Rewrite의 원 질문과 검색용 질문: 이번 실습은 1차 후보 검색(`Candidate Retrieval`) 단계 단독 검증이므로 `Q01`의 질문을 그대로 `payload["query"]`에 전달해 사용함
- Candidate ID → Rerank ID → Context included ID:
  - `candidate_ids` (`candidate_k=5`): `outputs/day27_04_live.json`의 `row.candidate_ids`에 기록된 시설 카테고리 후보 청크 목록 (최대 5건)
  - `Rerank ID` / `Context included ID` (`context_k=2`): 이번 실습은 1차 후보 수집 계약만 다루므로 Reranking과 Context 생성은 실행하지 않았으나, `candidate_k(5) >= context_k(2)` 계약을 분리해 후속 Reranker가 5개 후보를 평가한 뒤 상위 2개만 Context에 넣을 수 있도록 준비함
- 답변과 출처 문서의 실제 내용 대조: 최종 답변 생성(Generation) 전 단계이므로 답변–출처 대조 대상은 없으나, 반환된 모든 `Document` 객체에 6개 필수 메타데이터(`chunk_id`, `citation_id`, `doc_id`, `source_version`, `source_locator`, `category`)가 보존되어 있고 요청한 `category="시설"` 및 `d27_rag`의 최신 공개·권한 조건을 만족함을 확인함
- 실패 또는 예상과 다른 결과: `PYTHONUTF8=1 python -m pytest -q tests` 실행 시 `1 passed`로 통과. `--offline` 고정 예시와 `python main.py` 실제 RTX 5080 CUDA E5 + PostgreSQL(`d27_rag`) 검색 모두 오류 없이 `day27_04_fixture.json`과 `day27_04_live.json`을 생성함
- 고친 TODO와 이유:
  - `D27-04-B01` (`make_candidate_request`): `candidate_k`(1~20)와 `context_k`(1~3)를 서로 다른 제한값으로 분리해 검증하고 `candidate_k >= context_k` 조건을 강제하는 요청 `payload`를 반환하도록 구현함
  - `D27-04-B02` (`fetch_documents`): `retriever.invoke(payload)`로 후보 `Document` 목록을 수신한 뒤 반환 개수 상한(`<= candidate_k`), 6개 필수 출처 메타데이터 보존 여부, 요청 `category` 일치 여부를 검사하도록 구현함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): 1차 Bi-Encoder(E5) 검색에서 `candidate_k=5`로 넉넉히 후보를 가져오더라도 관련성이 가장 높은 청크가 1~2위 밖에 위치할 수 있으므로, 다음 실습(`05_cross_encoder_reranking`)에서 `(질문, 문서 본문)` 쌍을 GPU Cross-Encoder(`BAAI/bge-reranker-v2-m3`)로 직접 비교해 재정렬하면 상위 `context_k`의 정확도가 개선될 것으로 예상됨 (실측 검증 필요)