# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `05_cross_encoder_reranking` (Cross-Encoder Reranking)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **live** (`execution_mode: "live_e5_cuda_postgresql_crossencoder"`, `outputs/day27_05_live.json` 실측 완료 및 `outputs/day27_05_fixture.json` 사전 검증 완료)
- 요청 질문과 Category: `Q01` (`category: "시설"`) — 1차 E5+pgvector 검색 후보 5건에 대해 `BAAI/bge-reranker-v2-m3` (`device="cuda:0"`) 재정렬 수행
- Query Rewrite의 원 질문과 검색용 질문: 이번 실습은 검색 후 재정렬(`Cross-Encoder Reranking`) 단독 검증이므로 `Q01`의 질문을 그대로 `(question, doc.page_content)` 입력 쌍에 사용함
- Candidate ID → Rerank ID → Context included ID:
  - `before_ids` (1차 검색 후보 순위): `outputs/day27_05_live.json`의 `row.before_ids`에 기록된 E5 초기 검색 순위 5건
  - `after_ids` (Cross-Encoder 재정렬 순위): `row.after_ids`에 기록된 재정렬 후 순위 (`set(after_ids).issubset(before_ids)` 만족 — 후보 밖의 새 문서를 추가하지 않고 기존 후보의 순서만 재배치함)
  - `rerank_scores`: 각 문서 쌍의 모델 관련성 점수(`row.rerank_scores`)로 내림차순 정렬되었으며, 이 수치는 정답 확률(%)이 아닌 상대 순위 비교용 점수임을 확인함
- 답변과 출처 문서의 실제 내용 대조: 최종 답변 생성(Generation) 전 단계이므로 답변–출처 대조 대상은 없으나, 재정렬된 `Document` 목록에서 원본 `page_content`와 `chunk_id`·`citation_id`·`source_locator` 메타데이터가 유실되지 않고 `rerank_score`만 안전하게 추가되었음을 확인함
- 실패 또는 예상과 다른 결과: `PYTHONUTF8=1 python -m pytest -q tests` 실행 시 `1 passed`로 통과. `--offline` 고정 점수 예시에서는 초기 Top-2 밖에 있던 정답 청크가 재정렬 후 상위로 올라왔으며, `python main.py` 실측에서도 RTX 5080 CUDA GPU에서 `BAAI/bge-reranker-v2-m3`가 정상 로드·추론되어 `day27_05_live.json`이 생성됨
- 고친 TODO와 이유:
  - `D27-05-B01` (`create_pairs`): 빈 질문을 검증한 뒤 1차 검색 후보 `docs`의 각 본문(`doc.page_content`)을 `(question, doc.page_content)` 튜플 쌍 목록으로 변환하도록 구현함
  - `D27-05-B02` (`rank_documents`): `scorer(pairs)`가 반환한 점수의 개수 일치 여부와 유한성(`math.isfinite`)을 검증한 뒤, 원본 출처 메타데이터를 보존하면서 `rerank_score` 기준 내림차순으로 기존 후보만 재정렬하도록 구현함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): 개별 단계로 구현한 `Query Rewrite(02)` → `Retriever(04)` → `Cross-Encoder Rerank(05)` → `Context Builder`를 다음 실습(`06_langchain_integration`)에서 하나의 LangChain `Runnable` 파이프라인과 `State` 딕셔너리로 연결하면, 검색용 질문(`search_query`)과 답변용 원 질문(`question`), 그리고 실제 Context 포함 출처(`included_ids`)를 일관되게 추적할 수 있을 것으로 예상됨 (실측 검증 필요)