# 수행 기록 · Day28 실습 08

**실행한 모드:** `live` (`--offline` 및 `pytest` 계약 검증 통과 후, CUDA E5 · PostgreSQL `d27_rag` · GPU Cross-Encoder · OpenAI `gpt-4o-mini`로 상위 3개 질문 `--live` 실측 완료)

**작성 TODO:** `evaluate_one`, `summarize_all`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `--offline` 사전 검증에서는 전체 질문셋을 사용했고, `--live` 실측에서는 `dataset_version: "d28-eval-v1"`의 상위 3개 질문(`Q01`, `Q02`, `Q03`)을 `both`(`use_rewrite=True`, `use_rerank=True`) 경로로 실행함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. Target 실행에는 `target_inputs()`로 정제된 입력만 전달되었으며, `gold`와 `grades`는 실행 완료 후 `evaluate_one()` 단계에서 `question_id` 기준으로 사후 결합함

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 8`, `level: "01_basic"`, `mode: "live"`, `dataset_version: "d28-eval-v1"`) 실측 집계 결과:
    - 전체 요약(`summary`): `total_questions: 3`, `answerable_count: 3`, `no_answer_count: 0`, `recall_mean: 0.3333`, `ndcg_mean: 0.3333`, `error_count: 0`, `invalid_sources: 0`
    - 1차 Quality Gate: `precheck_passed: false` (`retrieval: false`, `ranking: false`, `citation: true`, `errors: true`)
    - 질문별 상세:
      - `Q01` → `status: "clarification_required"`, `ranked_ids: []`, `included_ids: []`, `recall_at_3: 0.0`, `ndcg_at_3: 0.0`
      - `Q02` → `status: "answered"`, `ranked_ids: ["FAC-102-C1", "FAC-103-C1", "FAC-109-C1", "FAC-107-C1", "FAC-101-C1"]`, `included_ids: ["FAC-102-C1", "FAC-103-C1"]`, `recall_at_3: 1.0`, `ndcg_at_3: 1.0`
      - `Q03` → `status: "clarification_required"`, `ranked_ids: []`, `included_ids: []`, `recall_at_3: 0.0`, `ndcg_at_3: 0.0`
- No-answer / 실패 / 정상의 차이:
  - 3개 질문 모두 시스템 오류(`has_error: false`)나 허위 출처(`invalid_sources: 0`)는 없었으나, `Q01`과 `Q03`이 `rewrite` 단계에서 `clarification_required`로 조기 중단되어 검색이 실행되지 않음으로써 `recall_mean: 0.3333`에 머물렀고 Quality Gate(`precheck_passed: false`)에서 정상적으로 차단됨
  - 모든 질문의 `generation_review`는 `"pending"`으로 기록되어 자동 Retrieval 지표만으로 생성 품질이 승인되지 않도록 분리함

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `evaluate_one()`에서 필수 Trace 필드(`ranked_ids`, `included_ids`, `answer`, `status`) 누락 시 빈 리스트로 대체하지 않고 `ValueError`를 발생시켜야 파이프라인 계약 위반이 조용히 묻히지 않음
  - `summarize_all()`에서 No-answer 질문을 평균 분모에서 제외하고 `no_answer_count`로 별도 집계하며, 검색·순위·출처·오류 4가지 관문을 `all()`로 묶어 하나라도 미달하면 `precheck_passed: false`로 차단해야 불안정한 RAG가 Agent Tool로 넘어가는 것을 막을 수 있음
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `Q01`·`Q03`이 `clarification_required`로 과도하게 조기 중단된 것이 `recall_mean: 0.3333` 하락의 직접 원인이므로, Retriever나 Reranker가 아니라 **`rewrite` Stage의 프롬프트 및 `needs_clarification` 판정 기준**을 우선 수정한 뒤 재평가해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - 현재 실측에서는 `precheck_passed: false`이므로 Agent Tool 등록을 보류하고 `rewrite` 과민 판정 문제를 먼저 해결해야 함
  - 1차 Quality Gate를 통과하더라도 이는 최소 관문일 뿐이므로, `generation_review: "pending"` 항목에 대한 `Faithfulness`·`Correctness` 사람 검수, No-answer 거절 동작, 권한 필터(`trusted_role`), 응답 지연(Latency) 기준까지 모두 확인한 뒤 Agent Tool로 연결해야 함