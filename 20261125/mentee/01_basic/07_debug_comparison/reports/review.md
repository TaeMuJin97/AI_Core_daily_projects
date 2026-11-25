# 수행 기록 · Day28 실습 07

**실행한 모드:** `live` (`--offline` 및 `pytest` 계약 검증 통과 후, CUDA E5 · PostgreSQL `d27_rag` · GPU Cross-Encoder · OpenAI `gpt-4o-mini`로 실제 `--live` 실행 완료)

**작성 TODO:** `score_delta`, `find_problem_stage`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `--offline` 사전 검증에서는 `Q01`, `Q07`, `Q06`(무정답) 3개 질문을 사용했고, 실제 토큰 비용이 발생하는 `--live` 실측에서는 `dataset_version: "d28-eval-v1"`의 `Q01` 1개 질문에 대해 `baseline`과 `rerank_only` 두 버전을 동일 조건(`k=3`)으로 비교함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. 두 버전 모두 `target_inputs()`로 정제된 질문·카테고리·히스토리만 Target에 전달했으며, `gold_chunk_ids`는 실행 완료 후 `evaluate_retrieval()`, `score_delta()`, `find_problem_stage()` 평가 단계에서만 사용함

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 7`, `level: "01_basic"`, `mode: "live"`, `dataset_version: "d28-eval-v1"`, `comparison_kind: "offline_version_comparison_not_online_AB"`) 실측 결과:
    - `Q01` → `baseline_recall: 1.0`, `rerank_recall: 1.0`, `delta_recall: 0.0`, `diagnosis: "ok"`
  - 참고: 6교시(`both`, `use_rewrite=True`) `--live` 실측에서 `Q01`이 빈 후보(`[]`)였던 것과 달리, `use_rewrite=False`인 7교시 `baseline`·`rerank_only`에서는 `Q01`의 `Recall@3`이 `1.0`으로 정상 통과함 → 6교시 `Q01` 문제의 원인이 Retriever/Reranker가 아니라 `rewrite` 단계에 있었음을 변인 통제 비교로 교차 확인함
- No-answer / 실패 / 정상의 차이:
  - `Q01`은 `baseline`에서 이미 정답(`FAC-102-C1`)이 Top-3 및 Context에 정상 포함(`diagnosis: "ok"`)되어 `rerank_only` 적용 후에도 `delta_recall: 0.0`으로 유지됨
  - `--offline`의 `Q06`처럼 무정답(No-answer) 질문은 `before`/`after`가 `None`이므로 `score_delta()`가 수치 차이(`0.0`)를 만들지 않고 `None`을 반환해 평균 변화량 왜곡을 방지함
  - 실패 시에는 `candidate_ids` 누락(`retrieval`) → `ranked_ids` 상위 탈락(`reranking`) → Context 컷오프(`context`) → 답변 근거 위반(`generation`) 순으로 원인을 분리 진단함

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `score_delta()`는 동일한 질문·Dataset 버전·실행 모드에서 한 번에 하나의 변수(`rerank_only`)만 바꿨을 때의 순수 변화량(`after - before`)을 측정하며, `None`을 숫자로 바꾸지 않아야 No-answer 질문이 변화량 집계에 섞이지 않음
  - `find_problem_stage()`는 파이프라인 앞단(`system_error` → `retrieval` → `reranking` → `context` → `generation`)부터 순차 진단해야, 후보 자체에 정답이 없는 문제를 Reranker나 Prompt 탓으로 오진하지 않음
  - 또한 이번 실험은 고정 질문셋에 두 버전을 실행하는 **오프라인 버전 비교(`offline_version_comparison_not_online_AB`)**이며 실사용자를 무작위 배분하는 온라인 A/B 테스트와 구분해야 함
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `delta_recall < 0`인 회귀(Regression)가 발생하거나 `diagnosis`가 `retrieval`이면 Query Rewrite·필터·임베딩·인덱스, `reranking`이면 Cross-Encoder 모델·`candidate_k`, `context`이면 `context_k`·글자 예산, `generation`이면 Prompt·출력 검증을 우선 수정함
  - 특히 `Q01` 단일 사례에서 `delta_recall=0.0`이 나온 것처럼 `Recall@3` 변화가 없더라도 Rerank 추가에 따른 지연 시간(Latency) 비용과 순위 변화(`MRR`/`nDCG`)를 다수 질문에서 함께 비교해 도입 여부를 결정해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - `Q01`이 `rewrite` ON(6교시)에서는 실패하고 OFF(7교시)에서는 통과한 것처럼, 특정 옵션 조합에서 생기는 회귀를 막기 위해 다수 질문에 대한 4종 조합(`baseline`, `rewrite_only`, `rerank_only`, `both`) 비교와 함께, CUDA 동기화 Latency 측정, `Faithfulness`·`Correctness`·권한 필터·출처 검증(`invalid_sources == 0`)을 모두 통과했는지 확인해야 함