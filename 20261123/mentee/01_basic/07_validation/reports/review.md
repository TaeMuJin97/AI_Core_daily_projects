# 실습 07 · 원문 대조 기록

- 선택한 수준: 01_basic
- 실행한 파일: main.py (결과 파일: outputs/validation_report.json)
- 실제 실행한 범위: 고정 입력 Validation / DB·Embedding·LLM 미실행 (`execution.mode: "offline"`, `db: false`, `embedding: false`, `llm: false`, `source_mode: "validation_fixtures"`)

## 공통 확인

1. **Context에 들어간 ID와 허용 ID는 각각 무엇인가요?**
   - **Context에 들어간 ID**: `outputs/validation_report.json`의 `context` 첫 줄 `[201] attendance_v2.md#sec-1`에 포함된 **`201`**입니다.
   - **허용 ID**: `allowed_source_ids(included_docs)`가 실제 `included_docs`에서 수집한 집합 **`{201}`**이며, JSON에는 정렬된 목록 `included_ids: [201]`로 기록되어 있습니다. 두 값이 정확히 일치합니다.

2. **normal 답변의 숫자·조건·예외를 지지하는 원문 문장을 그대로 적고 위치를 밝히세요.**
   - **원문 위치**: `[201]` `DOC-ATTEND` (`v2`, `attendance_v2.md#sec-1`, `outputs/validation_report.json`의 `context` 필드)
   - **원문 문장**: `"수업 시작 후 15분까지 입실하면 지각으로 기록합니다. 15분을 초과하면 결석으로 기록합니다. 단, 사전 승인을 받은 경우에는 운영실에 확인합니다."`
   - **자동 검사 vs 원문 대조 분리 기록**:
     - **자동(기계) 검사 결과**: `cases[0]`(`normal`)은 `outcome: "accepted"`, `error: null`, `status: "answered"`, `source_ids: [201]`, `human_review_required: true`로 형식·출처 규칙 검사를 통과함.
     - **사람의 원문 대조 결과**: 답변 `"일반 기준으로 15분까지는 지각입니다. 사전 승인을 받았다면 운영실에 확인합니다."`가 원문의 숫자 경계(`15분까지 지각`)와 예외 조건(`사전 승인 시 운영실 확인`)을 왜곡 없이 지지하고 있음을 직접 확인함.

3. **unknown_source는 어떤 단계에서 거절됐나요? 검색 후보에만 있던 ID도 허용해도 되나요?**
   - **거절 단계**: `inspect_case()`가 호출한 `receive_bundle()`의 4단계 업무·출처 규칙 검사(`validate_answer()`)에서 거절되었습니다. 모델이 제시한 `source_ids: [999]`가 허용 ID 집합 `provided_ids: {201}`의 부분집합인지 검사(`set(ids).issubset(provided_ids)`)할 때 `ValueError("source_not_provided")`가 발생했고, `receive_bundle()`이 이를 `RagServiceError("answer_validation_error")`로 변환해 `cases[2]`가 `outcome: "rejected"`, `error: "answer_validation_error"`, `result: null`, `human_review_required: false`로 기록되었습니다.
   - **검색 후보에만 있던 ID 허용 불가 이유**: 허용하면 안 됩니다. 검색 후보 목록에 있었더라도 글자 예산(`max_chars`)이나 개수 제한(`max_items`) 때문에 `build_context()`에서 탈락한 문서는 모델이 실제로 읽지 못한 자료입니다. 반드시 실제 Context에 들어간 `included_docs`의 ID만 허용 출처로 인정해야 근거 없는 인용을 차단할 수 있습니다.

4. **insufficient_context가 시스템 오류와 다른 이유를 적으세요.**
   - **`insufficient_context` (정상 업무 응답 → `accepted`)**: `cases[1]`(`insufficient`)처럼 검색·모델 호출·응답 파싱 파이프라인은 모두 정상 작동했지만, 제공된 자료에 질문에 답할 사실(예: 정확한 과제 마감 날짜)이 없을 때 정해진 규칙(`answer: "제공된 지식으로는 답할 수 없습니다."`, `source_ids: []`, `missing_information` 기재)에 따라 정직하게 응답한 **정상 승인 상태**입니다.
   - **시스템 오류 / 검증 실패 (장애·규칙 위반 → `rejected`)**: DB 장애, API timeout, 모델 거절(`provider_refusal`), 응답 미완료(`generation_not_completed`), 파싱 실패(`output_parsing_error`), 허용되지 않은 출처 인용(`answer_validation_error`) 등은 정상 응답을 만들지 못한 **실행·검증 실패(`RagServiceError`)**입니다. 이를 `insufficient_context`로 덮어쓰면 시스템 장애가 단순 정보 부족으로 숨겨져 원인 추적과 복구가 불가능해지므로 반드시 분리해 처리해야 합니다.

## 선택한 수준의 추가 확인

- `01_basic` (기본필수) 수준을 선택해 `normal`, `insufficient`, `unknown_source` 3개 공통 사례를 실행·검증함 (응용·심화 추가 항목은 해당 없음).
  - *(참고 개념 정리)*: `KnowledgeAnswer`는 `strict=True`와 `SourceID` 정수 제약을 두어 문자열 ID(`"201"`)는 스키마 단계에서 차단되고, 중복 ID(`[201, 201]`)는 `len(ids) != len(set(ids))`에서 `duplicate_source_ids`로 차단됨. 또한 `incomplete`는 `check_raw_message`에서 거절되는 시스템 오류이며, 출처 ID가 맞아도 원문 숫자를 틀린 `wrong_claim`은 기계 검사를 통과(`accepted`)할 수 있으므로 반드시 사람의 원문 대조(`human_review_required: true`)가 필요함.
  