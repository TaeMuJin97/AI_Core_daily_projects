# 실습 04 확인 기록

- 선택한 수준: 01_basic
- 실행일: 2026-11-23
- 실행 명령: python main.py
- 결과 파일: outputs/document_adapter.json
- 입력 출처와 실행한 구성요소: `input_source`는 `"lecture_fixture"`로, `coursekit.data.example_hit()`의 고정 예시 데이터(`DOC-ATTEND` v2, `citation_id: 201`) 1건을 입력으로 사용함. `--live-db` 없이 실행했으므로 실제 DB·임베딩·LLM은 호출하지 않았으며(`execution`: `mode: "local_adapter"`, `db: false`, `embedding: false`, `llm: false`), 로컬 변환 함수(`to_document`, `hits_to_documents`, `metadata_is_preserved`), 실제 `langchain_core.documents.Document` 객체, 그리고 `coursekit.data`, `coursekit.io`, `coursekit.reporting`만 실행함.

## 1. Document 생성 성공이 실제 검색 성공을 뜻하나요?

**아닙니다.** `Document` 생성 성공은 주어진 `Hit` 딕셔너리를 LangChain 규격(`page_content`, `metadata`)으로 손실 없이 옮기는 **어댑터 변환이 성공**했다는 뜻일 뿐, 실제 검색이 성공했다는 의미가 아닙니다.
- `outputs/document_adapter.json`을 보면 `documents[0]`의 `body_preserved: true`, `metadata_preserved: true`, `document_count: 1`로 변환은 성공했지만, `execution` 필드는 `mode: "local_adapter"`, `db: false`, `embedding: false`이고 `input_source`도 `"lecture_fixture"`입니다.
- 즉, E5 임베딩 모델이나 PostgreSQL+pgvector 검색(`coursekit.live.make_search_hits`)은 실행되지 않았습니다. 또한 실제 DB를 연동하더라도 현재 버전(`source_version`, `pipeline_version`), `ready`, `category` 필터 조건을 지키는 책임은 검색 SQL에 있으며, `Document` 변환 단계가 검색의 정확성을 대신 보장해 주지 않습니다.

## 2. citation_id를 항상 201로 넣으면 어떤 문제가 생기나요?

답변의 출처를 실제 원문 문서·청크와 정확히 연결하는 **출처 추적 계약이 완전히 깨집니다.**
- `outputs/document_adapter.json`의 `documents[0].citation_id`가 `201`(`citation_id_type: "int"`)인 것은 고정 예시 데이터(`DOC-ATTEND` v2)에서 온 값일 뿐, 실제 PostgreSQL DB가 발급하는 ID나 다른 문서(`DOC-ASSIGN`, `DOC-FACILITY`)의 ID와 같다고 가정할 수 없습니다.
- 만약 모든 문서에 `201`을 고정해 넣으면 ① 여러 청크의 ID가 충돌해 출처 인덱스 구성 시 중복 오류가 발생하고, ② 과제·시설 문서를 근거로 답했더라도 출처가 출석 문서(`201`)로 잘못 가리켜지며, ③ 서버가 허용된 실제 ID와 원문 위치(`source_locator`)를 대조해 검증하는 과정이 무력화됩니다. 따라서 반드시 입력 Hit가 가진 원래 정수 `citation_id`를 그대로 보존해야 합니다.

## 3. 빈 Hit 목록과 source_locator 누락은 왜 다르게 다루나요?

**정상적인 '검색 결과 없음' 상태**와 **필수 데이터 계약이 깨진 '오류' 상태**는 성격이 완전히 다르기 때문입니다.
- **빈 Hit 목록(`[]`)**: 특정 `category`나 질문에 맞는 문서가 DB에 없을 때 실제로 발생할 수 있는 **정상적인 결과**입니다. `hits_to_documents([])`가 가짜 문서를 만들지 않고 그대로 빈 목록 `[]`을 반환해야, 다음 단계에서 "근거가 없으므로 LLM 호출을 생략하고 정보 부족(`insufficient_context`)으로 응답"하는 안전한 분기를 탈 수 있습니다.
- **`source_locator` 누락**: `outputs/document_adapter.json`의 `metadata` 계약(`citation_id`, `chunk_id`, `doc_id`, `source_version`, `source_locator`, `category` 6개 필수 필드)이 깨진 **데이터 결함**입니다. 이를 `None`이나 빈 값으로 조용히 넘기면 나중에 답변의 원문 위치를 역추적할 수 없게 되므로, `to_document()`에서 `hit[key]`로 직접 접근해 즉시 `KeyError`를 발생시켜 원인을 바로 드러내야 합니다.