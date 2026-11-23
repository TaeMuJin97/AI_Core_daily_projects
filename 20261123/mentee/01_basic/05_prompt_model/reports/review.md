# 실습 05 · 원문 대조 기록

API Key나 비밀번호는 적지 않습니다. 실행 결과와 원문을 보고 빈칸을 채웁니다.

| 확인 항목 | 나의 기록 |
|---|---|
| 실행 명령 / 실행 종류 | `python main.py` / 실제 LLM 연동 실행 (`execution.mode: "live"`, `db: false`, `embedding: false`, `llm: true`) |
| 실제 모델 호출 여부와 확인 위치 | **호출함 (1회)** — `outputs/prompt_model.json`의 `execution.llm: true`, `real_model_calls: 1`, `fixed_example_calls: 0`, 그리고 `cases[0].response.usage_metadata` 및 `response_metadata`에서 실제 응답·토큰 사용 기록 확인 |
| 질문 / 사용한 원문 위치 | 질문: `"15분 늦으면 어떻게 기록되나요?"` (`cases[0].question`) / 원문 위치: `cases[0].evidence` (`doc_id: "DOC-ATTEND"`, `citation_id: 201`, `source_locator: "attendance_v2.md#sec-1"`) |
| 원문이 지지하는 답변 주장 | `cases[0].evidence.body` 원문("수업 시작 후 15분까지 입실하면 지각으로 기록합니다. 15분을 초과하면 결석으로 기록합니다. 단, 사전 승인을 받은 경우에는 운영실에 확인합니다.")에 근거해 **15분 입실은 '지각'**으로 기록되며, **15분 초과 시 결석**, **사전 승인을 받은 경우 운영실에 확인**한다는 주장과 출처 ID `[201]`이 원문과 일치함 |
| 원문에서 확인할 수 없는 정보 | 사전 승인 신청 절차·기한, 운영실 연락처·위치, 지각 누적 시 결석 전환 기준이나 감점 기준 등은 `cases[0].evidence.body` 원문에 적혀 있지 않아 답변에 임의로 추가할 수 없음 |
| Prompt 입력과 AIMessage의 차이 | **Prompt 입력**(`prompt_value_type: "ChatPromptValue"`, `prompt_messages`)은 `prompt.invoke(inputs)`가 로컬에서 `system`(답변 규칙·JSON 형식)과 `human`(질문·참고 자료) 메시지를 조립해 **모델에 보내기 전** 준비한 값임. 반면 **AIMessage**(`cases[0].response.type: "AIMessage"`)는 `chat_model.invoke(prompt_value)`로 실제 OpenAI API를 호출한 뒤 **모델이 생성해 돌려준** 응답 텍스트(`response.text`)와 호출 메타데이터(`response_metadata`, `usage_metadata`)를 담은 결과 객체임 |

## 아직 확인하지 못한 것

- `cases[0].human_evidence_review`가 `"pending"`인 것처럼, 이번 실습은 일반 `AIMessage` 텍스트를 눈으로 대조한 단계이며 **Pydantic 스키마 기반 Structured Output 파싱 검증(`WireAnswer` / `KnowledgeAnswer`)과 허용 출처 ID(`provided_ids`) 자동 검사**는 아직 연결하지 못함.
- 입력 데이터가 `coursekit.data.example_hit()`의 고정 예시(`citation_id: 201`) 1건이므로, **실제 E5 임베딩 + PostgreSQL(`pgvector`) 검색과 연결된 전체 RAG Chain** 동작 및 **근거가 부족한 질문(`insufficient_context`, 예: 과제 마감 날짜)**에서의 모델 응답 동작은 다음 실습에서 확인 필요함.