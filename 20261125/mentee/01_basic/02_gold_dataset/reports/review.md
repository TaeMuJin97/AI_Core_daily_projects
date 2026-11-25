# 수행 기록 · Day28 실습 02

**실행한 모드:** `offline_fixture` (실습 02는 외부 모델·DB를 호출하지 않는 고정 Gold Dataset 검증 전용)

**작성 TODO:** `select_gold`, `validate_gold_ids`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `dataset_version: "d28-eval-v1"`의 4개 질문(`Q01`, `Q05`, `Q06`, `Q07`)과 `corpus.json`을 입력으로 사용함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. `outputs/result.json`의 `target_example`을 확인한 결과 `{"question_id": "Q01", "question": "회의실 예약을 취소하는 방법은?", "category": "시설", "history": []}` 4개 필드만 포함되어 있으며 `gold_chunk_ids`가 Target 입력으로 누출되지 않았음을 확인함

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 2`, `level: "01_basic"`, `mode: "offline_fixture"`, `dataset_version: "d28-eval-v1"`)에서 4개 질문 모두 `valid_ids: true`로 통과함 (`pytest` 통과)
    - `Q01` → `["FAC-102-C1"]` (단일 정답, `valid_ids: true`)
    - `Q05` → `["ACA-101-C1"]` (단일 정답, `valid_ids: true`)
    - `Q06` → `[]` (무정답/No-answer, `valid_ids: true`)
    - `Q07` → `["FAC-104-C1", "FAC-102-C1"]` (복수 정답 2건, `valid_ids: true`)
- No-answer / 실패 / 정상의 차이:
  - `Q06`처럼 근거 문서가 없는 No-answer 질문은 `gold_chunk_ids`가 빈 리스트 `[]`이며, 중복이 없고 존재하지 않는 ID가 없으므로 유효한 레이블(`valid_ids: true`)로 유지하되 후속 Retrieval Recall 평균에서는 `None (N/A)`로 분리해 거절 성능 평가에 사용함
  - 반면 중복 ID가 들어가거나 `corpus.json`에 없는 삭제·오타 ID가 섞이면 `valid_ids: false`로 실패 처리해 평가 왜곡을 사전에 차단함

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - `len(ids) == len(set(ids))`로 중복을 막지 않으면 `|Gold|` 분모가 부풀려져 Recall@k가 왜곡되고, `set(ids).issubset(corpus.keys())`로 Corpus 존재 여부를 검사하지 않으면 실제로 검색될 수 없는 유령 청크 ID 때문에 검색 시스템이 부당하게 저평가됨
  - 또한 `Q07`처럼 한 질문에 여러 청크(`FAC-104-C1`, `FAC-102-C1`)가 동시에 정답일 수 있고, `Q06`처럼 정답이 없는 질문도 포함해야 환각 방지까지 평가할 수 있음
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `valid_ids: false`가 발생하면 검색 모델(Retriever)을 고치기 전에 먼저 **Gold Dataset 주석 파일(`gold_chunk_ids`)과 `corpus_version` 일치 여부, 인덱싱 누락 여부**를 데이터 검수 단계에서 수정해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - 평가셋(`corpus_version`)과 실제 서비스 DB(`d27_rag`)의 문서 버전이 일치하는지, `Q06` 같은 No-answer 질문에서 RAG Tool이 임의로 답하지 않고 `insufficient_context` 상태를 명확히 반환해 Agent가 환각 답변을 이어가지 않도록 차단하는지, 그리고 권한 필터(`trusted_role`)와 출처 ID 검증이 유지되는지 확인해야 함