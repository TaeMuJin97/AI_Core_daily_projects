# 실습 02 확인 기록

- 선택한 수준: 01_basic
- 실행일: 2026-11-23
- 실행 명령: python main.py
- 결과 파일: outputs/hit_context.json
- 입력 출처와 실행한 구성요소: `input_source`는 `"lecture_fixture"`로, `coursekit.data.example_hit()`의 고정 예시 데이터(출석 v2, `citation_id: 201`)를 사용함. 실제 DB·임베딩·LLM은 호출하지 않았으며(`execution`: `mode: "local_python"`, `db: false`, `embedding: false`, `llm: false`), 로컬 Python 함수(`format_hit`, `make_context`)와 `coursekit.data`, `coursekit.io`, `coursekit.reporting`만 실행함.

## 1. 본문과 ID를 같은 반복문에서 모으는 이유는 무엇인가요?

모델에게 실제로 전달한 본문(`context`)과 서버가 출처 검증에 사용할 허용 ID 목록(`included_ids`)을 100% 일치시키기 위해서입니다.
- `outputs/hit_context.json`을 보면 `context` 첫 줄에 `[201] attendance_v2.md#sec-1`과 원문 본문이 담겨 있고, `included_ids`에도 동일한 `[201]`이 기록되어 있습니다.
- 만약 검색 후보 전체에서 ID를 따로 모으고 Context는 별도로 추리면, Context에서 제외되어 모델이 읽지 않은 문서 ID까지 허용 출처로 남는 문제가 생깁니다. 따라서 `selected_hits`를 순회하는 같은 반복문 안에서 `format_hit(hit)`과 `hit["citation_id"]`를 함께 수집해야 합니다.

## 2. hits[:2]인데 한 건만 있는 경우 어떻게 되나요?

오류가 나지 않고 들어온 1건만 안전하게 선택되어 처리됩니다.
- 파이썬 리스트 슬라이싱 `hits[:2]`는 "앞에서 **최대** 2건"을 의미하므로, `main.py`처럼 1건(`[hit]`)만 넘기면 그대로 1건만 선택합니다.
- 실제 `outputs/hit_context.json`에서도 `context`에 `[201] attendance_v2.md#sec-1` 및 `"수업 시작 후 15분까지 입실하면 지각으로 기록합니다. 15분을 초과하면 결석으로 기록합니다. 단, 사전 승인을 받은 경우에는 운영실에 확인합니다."` 1개 블록만 들어가고, `included_ids`도 `[201]` 1건만 반환됩니다.
- 같은 원리로 빈 목록 `[]`이 들어와도 오류 없이 빈 문자열 `""`과 빈 목록 `[]`을 반환합니다.

## 3. len(context)는 Token 수인가요?

아닙니다. `outputs/hit_context.json`의 `character_count`에 기록된 `len(context)`는 단순 **문자(글자) 수**이며 LLM의 Token 수가 아닙니다.
- `len(context)`는 출처 ID(`[201]`), 원문 위치(`attendance_v2.md#sec-1`), 공백·줄바꿈, 원문 본문을 포함한 문자열 길이를 세는 값으로, Context 선택 과정을 관찰하기 위한 글자 예산 기준입니다.
- 한글 글자 수와 모델이 텍스트를 쪼개는 Token 수는 일치하지 않으므로, 실제 LLM 호출 시에는 해당 모델의 Tokenizer로 답변 규칙·질문·Context를 합친 입력 Token 길이와 출력 여유까지 별도로 확인해야 합니다.