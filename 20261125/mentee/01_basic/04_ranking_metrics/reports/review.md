# 수행 기록 · Day28 실습 04

**실행한 모드:** `offline_fixture` (실습 04는 외부 모델·DB를 호출하지 않는 고정 Baseline 순위 결과 기반 수식 검증 전용)

**작성 TODO:** `first_relevant_rank`, `calculate_rr`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `dataset_version: "d28-eval-v1"`의 3개 질문(`Q01`, `Q07`, `Q06`)에 대한 `baseline` 검색 순위(`ranked_ids`), 사전 고정 `gold_chunk_ids`, 그리고 `k=3`을 입력으로 사용함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. Target 실행에는 `target_inputs()`로 정제된 질문·카테고리·히스토리만 전달되었으며, `gold_chunk_ids`는 검색 실행 이후 `first_relevant_rank` 탐색과 `calculate_rr` 계산 단계에서만 비교에 사용됨

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 4`, `level: "01_basic"`, `mode: "offline_fixture"`, `dataset_version: "d28-eval-v1"`)에서 질문별 첫 정답 순위·RR 및 전체 MRR이 정상 산출됨 (`pytest` 통과)
    - `Q01` (단일 정답 `FAC-102-C1`): `first_rank: 3`, `rr_at_3: 0.3333333333333333` (`1/3`)
    - `Q07` (복수 정답 `FAC-104-C1`, `FAC-102-C1`): `first_rank: 2`, `rr_at_3: 0.5` (`1/2`, 첫 정답 `FAC-102-C1`의 순위만 반영)
    - `Q06` (무정답/No-answer, `gold=[]`): `first_rank: null`, `rr_at_3: null` (`None`, MRR 평균 집계 제외)
    - 전체 평균 `mrr_at_3`: `0.41666666666666663` (`(1/3 + 1/2) / 2 = 5/12 ≈ 0.417`)
- No-answer / 실패 / 정상의 차이:
  - `Q01`은 3교시 `Recall@3=1.0`으로 정답을 찾았지만 3위에 위치해 `RR@3=0.333`으로 낮게 평가된 반면, `Q07`은 `Recall@3=0.5`였지만 첫 정답이 2위에 있어 `RR@3=0.5`로 더 높게 평가됨
  - 답변 가능한 질문에서 Top-k 안에 정답이 없으면 `calculate_rr(None) = 0.0`으로 실패 점수가 MRR에 반영되지만, `Q06`처럼 애초에 정답 문서가 없는 No-answer 질문은 `rr_at_3: null`로 분리해 MRR 평균 분모(2개)에서 제외함 (만약 `Q06`을 `0.0`으로 합산하면 `mrr_at_3`가 `0.417`에서 `0.278`로 왜곡됨)

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `Recall@k`는 후보 안에 정답이 들어왔는지만 보므로, `context_k=2`처럼 상위 2개 문서만 LLM에 전달하는 RAG에서 `Q01`(3위)처럼 정답이 뒤로 밀리는 문제를 잡아내지 못함
  - `enumerate(..., start=1)`로 1-based 순위를 구해 `1 / rank`를 계산하면 상위 순위에 정답을 올릴수록 점수가 커지므로 Reranking 효과를 직접 측정할 수 있으며, 여러 정답의 관련성 등급(0/1/2)과 전체 정렬 품질까지 보려면 `nDCG@k`를 함께 사용해야 함
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `Q01`처럼 `Recall@3=1.0`(후보에 정답 있음)인데 `first_rank=3`으로 `MRR`이 낮은 경우, 1차 검색 후보 누락이 아니라 **순위 정렬 문제**이므로 **Cross-Encoder Reranker 모델·정렬 전략·`context_k` 설정**을 우선 점검해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - `MRR`이 높더라도 첫 정답 외 나머지 복수 근거 문서(`Q07`의 4위 `FAC-104-C1` 등)가 누락될 수 있으므로 `nDCG@k`·`Context Recall`과 함께, 생성 답변의 근거 일치(`Faithfulness`), 실제 `included_ids` 기반 출처 검증, 권한 필터(`trusted_role`), `Q06` 거절 처리 및 Rerank Latency 비용을 추가로 확인해야 함