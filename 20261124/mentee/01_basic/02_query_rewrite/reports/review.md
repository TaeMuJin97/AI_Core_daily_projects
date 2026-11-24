# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `02_query_rewrite` (Conversational Query Rewrite)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **live** (`execution_mode: "live_llm_api"`, `outputs/day27_02_live.json` 및 `offline_fixture` 사전 검증 `outputs/day27_02_fixture.json` 모두 확인)
- 요청 질문과 Category:
  - `Q02` (시설): 직전 대화(`History`)에서 `"회의실 예약"` 맥락을 가진 후속 질문
  - `Q04` (학사): 직전 대화 맥락이 포함된 후속 질문
  - `Q-ambiguous` (시설): `"그거는 어떻게 해?"` (`history: []`, 대상이 생략되고 이전 대화가 없는 모호한 질문)
- Query Rewrite의 원 질문과 검색용 질문:
  - `Q02`: `original_question` 원문은 그대로 보존하고, `History`에서 `"회의실 예약"` 대상을 복원한 독립 질문(`search_query`)을 별도 필드에 생성함 (`status: "ready"`, `needs_clarification: false`)
  - `Q04`: `original_question` 원문을 보존한 채 이전 대화 맥락이 반영된 독립 질문(`search_query`) 생성 (`status: "ready"`)
  - `Q-ambiguous`: `original_question`은 `"그거는 어떻게 해?"`로 유지하되, `history`가 비어 있어 대상을 확정할 수 없으므로 추측하지 않고 `status: "clarification_required"`, `search_query: null`, `needs_clarification: true`로 검색을 중단함
- Candidate ID → Rerank ID → Context included ID: 해당 없음 (이번 실습은 검색 전 단계인 Query Rewrite만 다루므로 Retriever·Reranker·Context 단계는 실행하지 않음)
- 답변과 출처 문서의 실제 내용 대조: 최종 답변 생성(Generation) 전 단계이므로 답변–출처 대조 대상은 없으나, 재작성된 `search_query`가 이전 `History`에 존재하는 대상(`회의실 예약` 등)만 복원하고 대화에 없는 날짜·숫자·조건을 임의로 추가하지 않았음을 원본 질문·History와 대조해 확인함
- 실패 또는 예상과 다른 결과: `PYTHONUTF8=1 python -m pytest -q tests` 실행 시 `1 passed`로 모든 계약 통과. 실제 LLM 호출 시에도 모호한 질문(`Q-ambiguous`)에 대해 임의의 대상을 지어내지 않고 `clarification_required`로 안전하게 분기됨을 확인함
- 고친 TODO와 이유:
  - `D27-02-B01` (`apply_rewrite`): 빈 질문 입력을 사전 검증한 뒤 `coursekit.rewrite.rewrite_query(question, safe_history, offline)`를 호출해 `--offline` 고정 예시와 실제 `ChatPromptTemplate | ChatModel` 호출 경로를 구분해 실행하도록 구현함
  - `D27-02-B02` (`record_rewrite`): `original_question`을 덮어쓰지 않고 별도 키로 보존하며, `needs_clarification`이 참이거나 독립 질문이 비어 있을 때 `status="clarification_required"` 및 `search_query=None`을 반환해 모호한 질문이 검색 단계로 넘어가지 않도록 차단함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): 복원된 단일 독립 질문(`Standalone Query`)이라도 문서 본문과 다른 동의어(예: *"예약 취소"* vs *"예약 철회"*)를 쓰는 경우 단일 질의 검색에서 누락될 수 있으므로, 다음 실습(`03_multi_query`)에서 원문을 포함한 복수 검색 질의를 생성해 후보 합집합(`chunk_id` 중복 제거)을 구성하면 후보 포함 범위가 넓어질 것으로 예상됨 (실제 효과는 03번 실행 결과로 검증 필요)