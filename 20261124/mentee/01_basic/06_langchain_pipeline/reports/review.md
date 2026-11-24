# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `06_langchain_pipeline` (LangChain Pipeline 통합)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **live** (`execution_mode: "live_e5_cuda_postgresql_llm"`, `outputs/day27_06_live.json` 실측 완료 및 `outputs/day27_06_fixture.json` 사전 검증 완료)
- 요청 질문과 Category: `Q02` (`category: "시설"`) — 대화 `History`가 포함된 후속 질문 (`candidate_k=5`, `context_k=2`, `use_rewrite=True`, `use_rerank=True`)
- Query Rewrite의 원 질문과 검색용 질문:
  - `trace.original_question`: `Q02`의 원래 질문 원문이 덮어쓰기 없이 그대로 보존됨
  - `trace.search_query`: 파이프라인 내부 `rewrite` Stage에서 대화 `History`를 바탕으로 복원한 독립 검색 질문이 별도 필드에 기록됨
- Candidate ID → Rerank ID → Context included ID:
  - `trace.candidate_ids`: E5(CUDA) + PostgreSQL(`d27_rag`) 1차 검색 후보 최대 5건
  - `trace.ranked_ids`: GPU Cross-Encoder(`BAAI/bge-reranker-v2-m3`)로 재정렬된 후보 ID 순서
  - `trace.included_ids`: `context_from_documents(..., context_k=2, max_chars=650)`로 실제 Context에 포함된 최종 출처 ID (최대 2건)
- 답변과 출처 문서의 실제 내용 대조: `outputs/day27_06_live.json`의 `result.answer`와 `result.source_ids`, 서버가 메타데이터로 연결한 `sources`의 원문 위치(`source_locator`)를 대조해 `result.source_ids`가 실제 Context에 포함된 `trace.included_ids`의 부분집합이며 응답 내용이 해당 근거 문서를 벗어나지 않음을 확인함
- 실패 또는 예상과 다른 결과: `PYTHONUTF8=1 python -m pytest -q tests` 실행 시 `1 passed`로 통과. `--offline`과 `python main.py` 실측 모두 `start | rewrite | multiquery | retrieval | rerank | context | generation` LCEL 체인이 정상 동작했으며, `trace.timing_ms`에 각 Stage별 소요 시간이 ms 단위로 분리 기록됨을 확인함
- 고친 TODO와 이유:
  - `D27-06-B01` (`prepare_pipeline_request`): `RagRequest` 계약에 맞춰 `case['question']`을 `query`에 담아 원 질문을 보존하고, `history`와 `use_rewrite=True`, `use_rerank=True`, `candidate_k=5`, `context_k=2`를 설정해 검색용 질문은 Chain 내부에서 생성되도록 구성함
  - `D27-06-B02` (`wire_langchain_pipeline`): `create_dependencies(offline)`로 주입받은 4개 함수(`rewrite`, `search`, `rerank`, `generate`)를 `create_rag_pipeline()`에 전달해 `.invoke()` 시점에 순차 실행되는 LCEL `Runnable` 파이프라인을 조립함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): 전체 파이프라인 통합 후에는 개별 변경(Baseline vs Rewrite vs Rerank)이 실제로 검색 순위와 Top-k 정답 포함 여부를 얼마나 바꿨는지 수치와 시간을 고정 조건에서 비교해야 하므로, 다음 실습(`07_compare_diagnose`)에서 동일한 후보·필터·정답 레이블(`gold_chunk_ids`)을 고정한 Before/After 비교 및 CUDA 동기화 Latency 측정을 수행해 효과를 검증할 계획임