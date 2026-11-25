# 수행 기록 · Day28 실습 03

**실행한 모드:** `offline_fixture` (실습 03은 외부 모델·DB를 호출하지 않는 고정 Baseline 검색 결과 기반 수식 검증 전용)

**작성 TODO:** `calculate_recall`, `count_gold_hits`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `dataset_version: "d28-eval-v1"`의 3개 질문(`Q01`, `Q07`, `Q06`)에 대한 `baseline` 검색 결과(`ranked_ids`)와 사전 고정 `gold_chunk_ids`, 그리고 `k=3`을 입력으로 사용함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. Target 실행에는 `target_inputs()`로 정제된 질문·카테고리·히스토리만 전달되었고, `gold_chunk_ids`는 검색 이후 `calculate_recall`과 `count_gold_hits` 평가 단계에서만 비교에 사용됨

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 3`, `level: "01_basic"`, `mode: "offline_fixture"`, `dataset_version: "d28-eval-v1"`)에서 3개 질문의 Top-3 지표가 정상 계산됨 (`pytest` 통과)
    - `Q01` (단일 정답 `FAC-102-C1`, `gold_count: 1`): `ranked_ids[:3]` = `["FAC-101-C1", "FAC-107-C1", "FAC-102-C1"]` → `hits_at_3: 1`, `recall_at_3: 1.0` (정답이 3위에 포함)
    - `Q07` (복수 정답 `FAC-104-C1`, `FAC-102-C1`, `gold_count: 2`): `ranked_ids[:3]` = `["FAC-101-C1", "FAC-102-C1", "FAC-107-C1"]` → `hits_at_3: 1`, `recall_at_3: 0.5` (`FAC-102-C1`은 2위로 포함되었으나 `FAC-104-C1`은 4위에 머물러 Top-3 밖으로 밀림)
    - `Q06` (무정답/No-answer, `gold_count: 0`): `ranked_ids: []` → `hits_at_3: 0`, `recall_at_3: null` (`None`, N/A)
- No-answer / 실패 / 정상의 차이:
  - `Q01`은 Top-3 내 정답을 모두 찾아 `Recall@3=1.0`, `Q07`은 2개 중 1개만 Top-3에 들어와 부분 포함(`Recall@3=0.5`)으로 계산됨
  - `Q06`은 관련 문서가 0개이므로 `0.0` 실패로 합산하지 않고 `null(None)`로 분리함 (만약 `Q06`을 `0.0`으로 넣으면 평균 Recall이 `0.75`에서 `0.50`으로 왜곡됨)

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `count_gold_hits`에서 `set(ranked[:k]) & set(gold)`를 사용해야 동일 청크 ID가 중복 반환되더라도 정답 개수가 부풀려지지 않음
  - `Recall@k`는 전체 정답 중 놓치지 않은 비율이므로 분모가 `k`가 아니라 전체 고유 Gold 개수(`|Gold|`)이며, `|Gold| == 0`인 무정답 질문은 수학적으로 나눌 수 없고 거절 성능 평가 대상이므로 `None`으로 분리해야 함
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `Q07`처럼 정답(`FAC-104-C1`)이 전체 검색 후보(`ranked_ids` 4위)에는 들어왔는데 Top-3에서 밀려 `Recall@3=0.5`가 된 경우라면, 1차 검색(Retriever)보다 **Cross-Encoder Reranker 또는 `context_k`·정렬 전략**을 우선 점검해야 함
  - 반대로 전체 후보(`ranked_ids`) 자체에 정답이 없다면 Query Rewrite·필터·임베딩·인덱스(Retriever)를 수정해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - `Recall@k`는 정답 포함 여부만 볼 뿐 정답이 1위인지 3위인지 순위 위치(`MRR`, `nDCG`)나 실제 답변의 근거 일치(`Faithfulness`), 출처 ID 유효성(`included_ids`), 권한 필터(`trusted_role`), `Q06` 같은 무정답 질문에서의 안전한 거절(`insufficient_context`) 여부를 보장하지 않으므로 이를 별도 검증한 뒤 Agent Tool로 연결해야 함