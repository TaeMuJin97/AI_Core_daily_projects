# 실습 01 확인 기록

- 선택한 수준: 01_basic
- 실행일: 2026-11-23
- 실행 명령: python main.py
- 결과 파일: outputs/rag_flow.json
- 입력 출처와 실행한 구성요소: 강의 고정 예시 데이터(`coursekit.data.example_hit()`, `DOC-ATTEND` v2 / `citation_id=201`)를 입력으로 사용했으며, 실제 DB·임베딩·LLM 호출 없이 로컬 Python 함수(`stage_order`, `evidence_note`)만 실행함(`execution`: `concept_review`).

## 1. Context와 Prompt는 어떻게 다른가요?

`outputs/rag_flow.json`의 `stages` 배열에서 두 단계의 역할과 입출력이 명확히 구분됩니다.
- **Context (`stages[1]`, `stage: "Context Builder"`)**: 검색으로 찾은 `후보 목록` 중에서 실제 답변에 사용할 근거 본문만 고르고, 허용 출처 ID(`선택한 근거·포함 ID`)를 함께 정리한 **참고 자료 자체**입니다.
- **Prompt (`stages[2]`, `stage: "Prompt"`)**: 위에서 만든 Context에 **답변 규칙**과 **사용자 질문**을 합쳐(`규칙·질문·Context`), LLM이 바로 읽을 수 있는 최종 **메시지(`모델이 읽을 메시지`)**로 구성한 입력입니다.
- 즉, Context는 모델에게 넘길 '선택된 근거 재료'이고, Prompt는 그 재료에 '질문과 처리 규칙'을 입혀 완성한 최종 모델 입력입니다.

## 2. 15분과 15분 초과가 다른 이유를 원문에서 찾으세요.

`outputs/rag_flow.json`의 `case.body` (`case.doc_id: "DOC-ATTEND"`, `case.source_version: "v2"`, `case.source_locator: "attendance_v2.md#sec-1"`) 원문에 시간 경계가 명확히 나뉘어 있기 때문입니다.
- **원문 확인**: `"수업 시작 후 15분까지 입실하면 지각으로 기록합니다. 15분을 초과하면 결석으로 기록합니다. 단, 사전 승인을 받은 경우에는 운영실에 확인합니다."`
- **경계 해석**: `"15분까지"`는 15분 정각을 포함하는 경계이므로 15분 입실은 `case.judgment`처럼 **지각**이고, `"15분을 초과하면"`은 15분을 넘어서는 시점부터이므로 **결석**으로 달라집니다.
- **예외 조건**: 또한 `case.exception`에 남긴 것처럼 **사전 승인을 받은 경우**에는 운영실에 확인하는 예외가 존재하므로, 답변 시 경계 표현(`까지`/`초과`)과 예외 조건을 함께 보존해야 합니다.

## 3. 이 JSON은 실제 LLM의 응답인가요?

**아닙니다.** 실제 LLM API나 DB를 호출한 결과가 아니라, 고정 예시 데이터로 RAG 흐름과 원문 근거를 사람이 직접 대조해 정리한 로컬 개념 확인 결과입니다.
- **`execution` 필드**: 실행 유형이 실제 모델 호출이 아닌 `"concept_review"`로 기록되어 있습니다.
- **`observation` 필드**: `"사람이 강의 원문을 읽고 작성한 역할·근거 확인표"`라고 명시되어 있습니다.
- **`case` 필드**: `coursekit.data.example_hit()`의 고정 예시 ID(`citation_id: 201`)와 원문(`attendance_v2.md#sec-1`)을 바탕으로 코드에 직접 작성한 판독 결과이므로, 실제 DB ID나 LLM 생성 응답과 동일하다고 가정하지 않습니다.