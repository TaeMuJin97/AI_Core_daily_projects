# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `07_before_after` (검색 개선 전후 비교)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **live** (`execution_mode: "live_e5_cuda_postgresql_crossencoder"`, `outputs/day27_07_live.json` 실측 완료 및 `outputs/day27_07_fixture.json` 사전 검증 완료 — 두 결과를 구분하여 기록)
- 요청 질문과 Category: `Q01` (`category: "시설"`) — 동일한 질문·필터(`role="learner"`, `candidate_k=5`)·Corpus 조건에서 Baseline(1차 검색)과 Cross-Encoder Reranking 전후를 비교함
- Query Rewrite의 원 질문과 검색용 질문: 이번 실습은 동일한 후보 집합(`Candidate Set`)에 대한 Reranking 효과를 분리해 비교하는 단계이므로 `Q01`의 원래 질문을 그대로 사용함
- Candidate ID → Rerank ID → Context included ID:
  - 사전 고정 `gold_ids`: `["FAC-102-C1"]` (`gold_in_candidates: true`)
  - `before_ids` (1차 E5 검색): `["FAC-102-C1", "FAC-107-C1", "FAC-109-C1", "FAC-103-C1", "FAC-101-C1"]` → `before_top_k (k=2)`: `["FAC-102-C1", "FAC-107-C1"]` (`before_in_top_k: true`, `before_best_rank: 1`)
  - `after_ids` (GPU Cross-Encoder 재정렬): `["FAC-102-C1", "FAC-109-C1", "FAC-107-C1", "FAC-103-C1", "FAC-101-C1"]` → `after_top_k (k=2)`: `["FAC-102-C1", "FAC-109-C1"]` (`after_in_top_k: true`, `after_best_rank: 1`, `order_changed: true` — 2위 `FAC-107-C1`과 3위 `FAC-109-C1` 순위 교체)
  - 참고: `offline_fixture`(`day27_07_fixture.json`)는 의도적으로 정답이 초기 Top-2 밖에 있는 고정 사례로 비교 로직만 검증했으며 실제 성능으로 해석하지 않음
- 답변과 출처 문서의 실제 내용 대조: 최종 답변 생성(Generation) 전 단계이므로 답변–출처 대조 대신, 사전 정의된 평가 전용 `gold_ids` (`["FAC-102-C1"]`)가 검색 함수에 전달되지 않았고 비교 판정에만 사용되었음을 확인함. 전후 모두 Top-2에 정답이 포함되었으나 2위 문서 교체(`FAC-107-C1` → `FAC-109-C1`)가 실제 답변 Grounding에 미치는 영향은 생성 단계에서 별도 대조가 필요함
- 실패 또는 예상과 다른 결과: `PYTHONUTF8=1 python -m pytest -q tests` 실행 시 `1 passed`로 통과(`comparison['k'] == 2`). 실측 결과 정답(`FAC-102-C1`)은 전후 모두 1위로 유지되었으나, `search_ms`는 `374.437ms`인 반면 CUDA 동기화(`cuda=True`)가 적용된 `rerank_ms`는 `4516.89ms`(약 12배)가 소요됨. 순위가 일부 바뀌었더라도 추가 Latency 대비 효용을 단일 질문만으로 단정할 수 없음을 확인함
- 고친 TODO와 이유:
  - `D27-07-B01` (`compare_rankings`): 동일한 후보 목록(`before`, `after`)과 사전 고정된 `gold`를 받아 `k=2` 기준 Top-2 포함 여부(`before_in_top_k`, `after_in_top_k`), 후보 존재 여부(`gold_in_candidates`), 최고 순위 변화(`before_best_rank`, `after_best_rank`) 및 순서 변경 여부(`order_changed`)를 구조화된 dict로 반환하도록 구현함
  - `D27-07-B02` (`interpret_change`): 순위 변동(`order_changed=True`)만으로 개선을 단정하지 않고, Recall Ceiling·Top-2 진입·회귀·유지 상태를 구분하며 추가 Rerank 지연 시간(Latency) 대비 효용과 실제 답변 Grounding·Day28 정량 평가의 필요성을 명시하도록 구현함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): 단일 질문 Before/After 비교에서 Reranker 추가 시 Latency 증가(`4516.89ms`)가 확인되었으므로, 모델 사전 로딩(Warm-up) 이후 반복 측정과 Day 28의 다수 질문 평가(`Recall@k`, `MRR`, `nDCG`)를 통해 실제 효용을 검증해야 함. 우선 다음 마지막 실습(`08_enhanced_rag_api`)에서 개선된 파이프라인을 FastAPI 엔드포인트(`/api/v1/rag/answer`)와 연결해 정상 응답(`200`), 입력 계약 위반(`422`), 내부 Stage 실패(`502`) 분리를 검증할 계획임