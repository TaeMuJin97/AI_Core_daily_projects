# 수행 기록 · Day28 실습 06

**실행한 모드:** `live` (`--offline` 및 `pytest` 계약 검증 통과 후, CUDA E5 · PostgreSQL `d27_rag` · GPU Cross-Encoder · OpenAI `gpt-4o-mini`로 실제 `--live` 실행 완료 / `LANGSMITH_TRACING=false` 로컬 평가)

**작성 TODO:** `safe_target_input`, `invoke_target`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `dataset_version: "d28-eval-v1"`의 상위 3개 질문(`Q01`, `Q02`, `Q03`)을 대상으로 `both`(`use_rewrite=True`, `use_rerank=True`) 경로를 실행함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. `safe_target_input()`에서 `question_id`, `question`, `category`, `history` 4개 키만 새 `dict`로 화이트리스트 복사해 `gold_chunk_ids`, `relevance_grades`, `reference_answer`가 `Runnable.invoke()` 입력으로 전달되지 않도록 차단함

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 6`, `level: "01_basic"`, `mode: "live"`, `dataset_version: "d28-eval-v1"`, `langchain_runnable: true`)에서 3개 질문 모두 `source_mode: "live"`로 실행됨
    - `Q01` → `ranked_ids: []`, `included_ids: []` (실측 실행에서 빈 후보/Context 반환)
    - `Q02` → `ranked_ids`: `["FAC-102-C1", "FAC-103-C1", "FAC-109-C1", "FAC-107-C1", "FAC-101-C1"]` → `included_ids`: `["FAC-102-C1", "FAC-103-C1"]` (Top-2 포함, `FAC-102-C1` 1위)
    - `Q03` → `ranked_ids`: `["FAC-102-C1", "FAC-109-C1", "FAC-107-C1", "FAC-103-C1", "FAC-101-C1"]` → `included_ids`: `["FAC-102-C1", "FAC-109-C1"]` (Top-2 포함, `FAC-102-C1` 1위)
- No-answer / 실패 / 정상의 차이:
  - 초기 `--live` 실행 시 `.env` 모델의 `temperature=0.0` 미지원으로 `StageError(rewrite:OpenAIInvalidRequestError)`가 발생해 정상 응답이나 정보 부족으로 위장되지 않고 즉시 실패로 격리됨 (`LLM_MODEL=gpt-4o-mini` 변경 후 정상 실행)
  - `Q02`·`Q03`은 정상적으로 5건 재정렬 및 Top-2 Context 선택이 완료된 반면, `Q01`은 `ranked_ids: []`, `included_ids: []`로 반환됨 — 실제 LLM의 비결정적 출력으로 `rewrite` 단계에서 `clarification_required`로 조기 중단되었거나 검색 필터/질의 변환 결과 후보가 0건이었을 가능성이 있으므로, 단순 `No-answer`로 단정하지 않고 `trace.status`·`search_query`를 추가 추적해야 함

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `safe_target_input()`을 화이트리스트 복사로 구현해야 평가셋에 새 정답 필드가 추가되더라도 Target으로 누출(Gold Leakage)되지 않음
  - `invoke_target()`에서 일반 함수 직접 호출 대신 `target.invoke(request)`를 사용하고 반환 타입(`dict`) 및 `question_id` 일치를 검증해야, 체인 정의 시점과 실제 모델·DB 호출 시점을 분리하고 배치 평가 중 질문 간 결과가 뒤섞이는 오류를 방지할 수 있음
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `Q01`처럼 `ranked_ids`와 `included_ids`가 모두 빈 경우는 Reranker나 Generator 문제가 아니라 앞단 실패이므로, 먼저 **`rewrite` Stage의 판정(`needs_clarification` 과민 반응 여부 및 `search_query`)**과 **`retrieval` Stage의 필터·검색 조건**을 Trace에서 확인해 수정해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - `Q01`처럼 정상 질문이 빈 결과(`[]`)를 반환했을 때 Agent가 이를 "관련 규정 없음"으로 오해하고 잘못 답하지 않도록, `clarification_required`·`insufficient_context`·`system_error` 상태를 명확히 구분해 반환하는 출력 계약과 `temperature` 등 모델 호환성·예외 처리, 권한 필터(`trusted_role`) 및 출처 검증을 함께 확인해야 함