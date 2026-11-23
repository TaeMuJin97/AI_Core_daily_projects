# 실습 03 확인 기록

- 선택한 수준: 01_basic
- 실행일: 2026-11-23
- 실행 명령: python main.py
- 결과 파일: outputs/object_contracts.json
- 입력 출처와 실행한 구성요소: `main.py` 내부에 정의된 고정 입력 표(`COMPONENT_INPUTS`)를 사용했으며, 실제 DB·임베딩·LLM 호출 및 LangChain 객체의 `.invoke()`는 전혀 실행하지 않음(`execution`: `mode: "concept_review"`, `db: false`, `embedding: false`, `llm: false`, `observation`: `"입력·출력 대응표; Prompt·모델 invoke는 실행하지 않음"`). 로컬 Python 함수(`component_outputs`, `access_kinds`)와 `coursekit.io`, `coursekit.reporting`만 실행함.

## 1. 같은 invoke인데 Prompt와 Chat Model은 무엇이 다른가요?

`outputs/object_contracts.json`의 `components` 배열을 보면 두 구성요소 모두 `access: "invoke"`로 공통 실행 방식을 사용하지만, **실제로 수행하는 작업과 입출력, 외부 API 호출 여부**가 완전히 다릅니다.
- **Prompt (`components[2]`)**: `input`으로 `"question·context가 있는 dict"`를 받아 `output`으로 **`"ChatPromptValue"`**를 반환합니다. 로컬(내 컴퓨터)에서 템플릿 변수만 채워 모델에 보낼 메시지 묶음을 조립할 뿐, 외부 LLM API를 호출하지 않습니다.
- **Chat Model (`components[3]`)**: `input`으로 `"ChatPromptValue 또는 메시지 목록"`을 받아 `output`으로 **`"AIMessage"`**를 반환합니다. 이 단계에서 비로소 외부 LLM API에 실제 요청을 보내 답변을 생성합니다.
- 즉, `invoke`는 실행 방식(인터페이스)을 통일한 이름일 뿐이며, 어떤 객체의 `invoke`인지에 따라 로컬 메시지 작성인지 외부 모델 호출인지가 달라집니다.

## 2. Document에서 본문을 읽는 표현은 무엇인가요?

**`doc.page_content`** (객체의 `page_content` 속성 읽기)입니다.
- `outputs/object_contracts.json`의 `components[0]`(`component: "Document"`)을 보면 `access`가 `"invoke"`가 아니라 **`"data"`**로 표시되어 있고, `input`/`output`에 `page_content`와 `metadata`를 담아 본문·출처를 보관하는 객체라고 정의되어 있습니다.
- `Document`는 작업을 실행하는 Runnable이 아니라 검색 결과를 담아두는 데이터 보관함(택배 상자)이므로 `.invoke()`를 호출하지 않고, 본문은 **`doc.page_content`**, 출처 ID·원문 위치 등은 **`doc.metadata["citation_id"]`**처럼 속성으로 꺼내 읽습니다.

## 3. Document 목록을 question·context가 필요한 Prompt에 그대로 전달해도 되나요?

**안 됩니다.** 앞 단계의 출력 형식과 다음 단계의 입력 형식(입출력 계약)이 서로 맞지 않기 때문입니다.
- `outputs/object_contracts.json`에서 `Retriever`(`components[1]`)의 `output`은 **`"list[Document]"`**인 반면, `Prompt`(`components[2]`)의 `input`은 **`"question·context가 있는 dict"`**입니다.
- LangChain의 `|` 연결 기호는 앞뒤의 자료형을 자동으로 변환해 주지 않으므로, `list[Document]`를 바로 `Prompt`에 넘기면 오류가 발생합니다.
- 따라서 중간에 Context Builder 단계를 두어 선택한 `Document`들의 본문과 출처 ID를 문자열 `context`로 정리하고, 원래 질문과 함께 `{"question": ..., "context": ...}` 형태의 `dict`로 묶은 뒤 `Prompt`에 전달해야 합니다.