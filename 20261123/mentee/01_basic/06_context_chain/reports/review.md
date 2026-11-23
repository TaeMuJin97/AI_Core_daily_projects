# 실습 06 · 원문 대조 기록

API Key나 비밀번호는 적지 않습니다. 실행 결과와 원문을 보고 빈칸을 채웁니다.

| 확인 항목 | 나의 기록 |
|---|---|
| 실행 명령 / 실행 종류 | `python main.py` / 실제 LLM 연동 실행 (`execution.mode: "live"`, `db: false`, `embedding: false`, `llm: true`) |
| 실제 모델 호출 여부와 확인 위치 | **호출함 (1회)** — `outputs/context_chain.json`의 `execution.llm: true`, `real_model_calls: 1`, `bundle.raw.type: "AIMessage"`, `bundle.raw.response_metadata` 및 `bundle.raw.usage_metadata`에서 실제 모델 응답과 토큰 사용 기록 확인 |
| 질문 / 사용한 원문 위치 | 질문: `"15분 늦으면 어떻게 기록되나요?"` (`prompt_input.question`) / 원문 위치: `included_sources`의 학사 문서 2건 — `[201]` `DOC-ATTEND` v2 (`attendance_v2.md#sec-1`), `[202]` `DOC-ASSIGN` v1 (`assignment.txt`). 이 중 답변의 직접 근거는 `[201]` 출석 규정 원문 |
| 원문이 지지하는 답변 주장 | `context`의 `[201] attendance_v2.md#sec-1` 원문("수업 시작 후 15분까지 입실하면 지각으로 기록합니다. 15분을 초과하면 결석으로 기록합니다. 단, 사전 승인을 받은 경우에는 운영실에 확인합니다.")에 근거해 **수업 시작 후 15분까지 입실은 지각**, **15분 초과 시 결석**, **사전 승인 시 운영실에 확인**한다는 내용과 출처 ID `[201]`(`observed_source_ids`)이 원문과 일치함 |
| 원문에서 확인할 수 없는 정보 | 사전 승인 신청 절차·마감 기한, 운영실 연락처·위치, 지각 누적 시 감점·결석 전환 기준 등은 `context`에 포함된 `[201]`·`[202]` 원문에 없어 답변에 임의로 추가할 수 없음 (함께 포함된 `[202]` 과제 제출 안내는 출석 기준 질문과 무관함) |
| 검색 후보 ID와 실제 포함 ID의 차이 | **검색 후보 ID**는 검색 조건(`category`, `candidate_k`)으로 찾아온 전체 후보 목록의 ID이고, **실제 포함 ID(`included_ids` / `provided_ids`)**는 `build_context()`에서 중복 `chunk_id` 제거·글자 예산(`max_chars=600`)·개수 상한(`max_items=2`)을 통과해 모델 `context`에 실제로 들어간 `included_docs`에서만 뽑은 ID임. 이번 실행에서는 학사 문서 2건이 모두 예산 안에 들어가 `included_ids: [201, 202]`가 되었지만, 예산·개수 제한으로 탈락한 후보는 모델이 읽지 않았으므로 허용 출처에서 반드시 제외해야 함 |
| raw·parsed·parsing_error 각각의 의미 | `with_structured_output(WireAnswer, method="json_schema", strict=True, include_raw=True)`가 반환하는 `bundle`의 3개 필드임.<br>- **`raw`**: 모델이 돌려준 원본 `AIMessage` (원본 텍스트, 완료 상태 `status`, 거절 `refusal` 여부, 토큰 사용량 `usage_metadata` 확인용)<br>- **`parsed`**: 응답을 `WireAnswer` 4필드(`status`, `answer`, `source_ids`, `missing_information`) 스키마로 파싱한 구조화 객체 (파싱 실패·거절 시 `null`)<br>- **`parsing_error`**: 스키마 파싱 과정에서 발생한 오류 정보 (정상 파싱 시 `null`) |

## 아직 확인하지 못한 것

- `source_id_membership_only`는 모델이 인용한 ID가 `included_ids`(`[201, 202]`)에 포함되는지만 단순 관찰한 값이며, `raw`의 거절(`refusal`)·미완료(`incomplete`) 검사, `parsing_error` 차단, `KnowledgeAnswer` 기반 상태별 규칙(`answered` vs `insufficient_context`) 승인 검증은 실습 07에서 구현·검증해야 함.
- `human_evidence_review`가 `"pending"`인 것처럼 ID 포함 여부 관찰만으로는 답변 내용의 사실성(Grounding)이 자동 보장되지 않으므로, 문장 속 숫자·경계(`까지`/`초과`)·예외 조건은 원문과 별도로 대조해야 함.
- 입력 문서가 `coursekit.data.load_hits()`의 고정 예시(`201`, `202`)이므로, 실제 E5 임베딩 + PostgreSQL(`pgvector`) 검색과 연결된 전체 RAG 파이프라인 및 FastAPI 응답 연동은 이후 실습에서 확인 필요함.