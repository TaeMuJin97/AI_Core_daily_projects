# Day 21. LLM 입출력 제어 파이프라인 설계 및 회고 (AI 지식 답변 생성기 v1)

## 1. 들어가며: 왜 모델 호출 자체보다 '앞뒤 파이프라인'을 먼저 만들었는가?

LLM을 연동한 서비스를 구상할 때 가장 빠지기 쉬운 함정은 프롬프트 문구 몇 줄을 감각적으로 고치면서 모델이 알아서 완벽한 답을 주길 기대하는 것이다. 하지만 실제 백엔드 환경(FastAPI + PostgreSQL)에 LLM을 올리려면, 모델 호출은 전체 시스템의 일부일 뿐 그 앞단(Input Assembly)과 뒷단(Output Validation & Retry Control)을 결정론적인(Deterministic) 코드로 통제해야 한다.

오늘 실습(01~08)은 외부 API나 RAG(벡터 검색)를 붙이기 전에, 모델 호출의 앞과 뒤에서 엔지니어가 통제해야 할 입출력 규격과 평가 체계를 밑바닥부터 조립해 본 과정이었다. 내가 이해한 전체 아키텍처의 흐름을 4단계로 정리해 둔다.

---

## 2. 전체 파이프라인 아키텍처 (4단계 흐름)

```text
[사용자 질문] 
   │
   ▼
[1. 입력 구성 (01~04)] ── 고정 스냅샷 ID 선택·직렬화(예산 관리) + 6요소 프롬프트 안전 조립
   │
   ▼
[LLM 응답 수집] ───────── 수동 응답 관찰(manual_chat) / 제어 흐름 검증용 샘플(fixture)
   │
   ▼
[2. 출력 검사 (06)] ───── 1단계(JSON 문법) → 2단계(Pydantic Schema) → 3단계(출처 범위·상태 규칙)
   │
   ├─ (형식 오류: json_error / schema_error) ──► [3. 제한된 재시도 (07)] (최대 1회 수정 요청, 총 호출 <= 2)
   ├─ (참조·규칙 위반: unknown_source 등)   ──► [즉시 중단 (Stop)] (억지 재시도 방지, None 반환)
   │
   ▼ (자동 검증 통과: answered 및 정상 insufficient_context)
[4. 사람의 근거 대조 & A/B 평가 (05, 08)] ── 의미적 정합성(evidence_ok) 최종 확인 및 Dev/Holdout 분리 평가
```

---

## 3. 단계별 핵심 설계 포인트와 내가 이해한 원리

### Step 1. 입력 구성: Context 예산 관리와 안전한 프롬프트 조립 (`01` ~ `04`)

- 안전한 템플릿 치환 (`01_prompt_structure`)
  - 파이썬 기본 `.format()`은 사용자 질문이나 JSON 예시 안에 `{}` 중괄호가 들어있으면 즉시 `KeyError`를 일으킨다. 실무에서는 입력 텍스트에 어떤 기호가 들어올지 예측할 수 없으므로 `string.Template`과 `safe_substitute`를 사용해 지정된 `$변수`만 안전하게 치환하도록 방어했다.
- 예제 오염 방지 (`02_examples_versions`)
  - Few-shot 예제를 줄 때 실제 운영 지식 ID(`101~103`)를 그대로 쓰면, 모델이 예제의 형식만 배우는 게 아니라 예제 속 출처 번호까지 그대로 복사해 답하는 문제가 생긴다. 이를 막기 위해 예제 전용 ID를 `901`로 완전히 분리했다. 만약 실제 답변에 `901`이 찍히면 뒷단 검증기에서 곧바로 잡아낼 수 있다.
- 추측 차단과 상태 정의 (`03_task_decomposition`)
  - 복합 질문에서 요구하는 사실 중 하나라도 제공된 지식에 없다면, 아는 부분만 어설프게 섞어 답하지 않고 `status="insufficient_context"`로 명확히 멈추도록 설계했다. 이때 정보 부족은 시스템 에러나 모델의 안전 정책 거절(Refusal)이 아니라, 주어진 문맥 안에서 내릴 수 있는 정상적인 비즈니스 판단 결과다.
- Context Window 예산과 `margin = 256`의 의미 (`04_context_builder`)
  - DB에 있는 지식을 전부 프롬프트에 쏟아붓는 대신, 필요한 ID만 순서대로 골라 JSON으로 직렬화했다.
  - 특히 전체 윈도우(`8,192`)에서 지시·질문(`800`), 예제(`600`), 출력 예약(`1,600`)을 빼고도 `margin = 256`($2^8$)을 별도로 남겨두는 점이 인상적이었다. JSON 직렬화 기호(`{}`, `""`), 메시지 구분자 태그, 한글 토크나이징 오차로 인해 발생하는 숨은 오버헤드를 이 256 토큰의 버퍼가 흡수해 주어야 입력 문맥이 잘리거나(Truncation) 출력 JSON이 중간에 끊기는 사고를 막을 수 있다.

### Step 2. 출력 검사: 왜 검증기를 3단계(+사람 검토 1단계)로 쪼갰는가? (`06_output_validation`)

모델이 뱉은 문자열을 하나로 뭉뚱그려 검사하면 실패했을 때 '어떻게 대응할지' 결정할 수 없다. 그래서 검증 파이프라인을 역할별로 분리했다.

1. `json_error`: `strict_json`을 통한 문법 및 중복 키 검사
2. `schema_error`: Pydantic `ConfigDict(extra="forbid", strict=True)`를 통한 엄격한 타입 검사. `"101"` 같은 문자열이나 `true`가 정수 `1`로 자동 형변환(Type Coercion)되어 통과하는 것을 로컬에서 차단한다.
3. `check_rules` (`unknown_source`, `duplicate_source`, `status_rule`, `blank_answer`): 문법과 타입이 맞아도 비즈니스 논리가 깨진 경우를 잡는다. 특히 DB 전체에 존재하는 ID라도 '이번 요청의 문맥(`provided_ids`)'에 넣어주지 않았다면 인용할 수 없도록 막았다.
4. `semantic_counterexample` (자동 검증의 한계): 문맥에 `[101, 102, 103]`을 다 넣어줬을 때, 모델이 102번 내용으로 답하면서 출처에 `[101]`을 적어내면 1~3단계 자동 검증은 모두 통과(`error=None`)한다. 결국 인용된 본문이 실제 주장을 뒷받침하는지(`evidence_ok`)는 사람의 검토 영역으로 남겨두어야 하며, 자동 통과 직후에는 `True`가 아니라 `None`(미평가)으로 두는 이유를 명확히 이해했다.

### Step 3. 제한된 재시도(Bounded Retry)와 손절매 기준 (`07_bounded_retry`)

선물 거래나 리스크 관리에서 손절(Stop-loss) 라인 없이 무한 물타기를 하면 계좌가 터지듯, LLM 호출에서도 `while True`로 성공할 때까지 무한 재시도를 돌리면 API 비용과 지연 시간(Latency)이 폭발한다.

- 재시도 허용 (`calls = 2`): `json_error`나 `schema_error`처럼 괄호가 깨졌거나 필드 형식을 놓친 경우에는 안전한 한 줄 요약(`[수정 요청]`)만 붙여 딱 1번만 더 기회를 준다 (`for attempt in (1, 2):`). 이때도 깨진 원문 전체나 파이썬 Traceback을 프롬프트에 그대로 붙이지 않는 화이트리스트 방식을 쓴다.
- 즉시 중단 (`calls = 1`): `unknown_source`나 `status_rule` 위반은 프롬프트에 없는 근거를 지어낸 것이므로, 같은 문맥으로 다시 물어본다고 없던 사실이 생기지 않는다. 재시도 없이 1회에 즉시 중단하고 `(None, history)`를 반환한다.
- 정상 종료 (`calls = 1`): 규칙에 맞는 `insufficient_context`는 실패가 아니므로 1회에 즉시 통과시킨다.
- 모든 시도는 성공/실패 여부와 상관없이 `prompt_sha256` 해시 지문과 함께 `history`에 남겨 첫 응답 품질과 재시도 복구율을 분리해 추적할 수 있게 했다.

### Step 4. Dev / Holdout 분리와 A/B 평가 (`05_ab_evaluation`, `08_daily_project`)

- 변인 통제: 기준안 A(`BASE_RULE`)와 변경안 B(`BASE_RULE + ADDED_RULE`)를 비교할 때 질문, 문맥, 스키마, 예제 유무(0개)를 모두 고정하고 오직 '근거 부족 처리 규칙 1줄'만 바꿨다.
- 과적합 방지: `05`교시에서는 개선용 세트(`D01~D03`)로 프롬프트를 설계해 `frozen_bundle.json`으로 동결(Freeze)하고, `08`교시에서는 아껴둔 최종 확인용 세트(`H01~H03`)를 사용해 검증했다.
- 정직한 지표 집계: 첫 응답(`attempt == 1`)을 기준으로 미실행(`not_run`), 자동 검증 실패(`False`), 사람 미평가(`None`)를 0점이나 통과로 섞지 않고 각각의 건수로 투명하게 리포팅하도록 구현했다.

---

## 4. 실행 및 검증 방법 (`08_daily_project`)

```bash
# 1. 05교시 동결 번들을 사용한 Holdout(H01~H03) 프롬프트 준비
python main.py prepare --run holdout_01 --bundle ../05_ab_evaluation/outputs/dev_01/frozen_bundle.json

# 2. 수집된 응답 검증 및 summary.md 리포트 생성
python main.py review --run holdout_01

# 3. Fixture 기반 4대 시나리오 호출 수([2, 2, 1, 1]) 제어 흐름 검증
python main.py fixtures
```

---

## 5. 다음 단계 연결 (Day 22~)

오늘 구축한 입출력 검증기(`06`)와 제한된 재시도 제어기(`07`)는 일급 함수(`generate`, `validate` 콜백 주입) 구조로 설계되어 있다. 덕분에 내일 이어질 실제 LLM API 연동이나 향후 RAG(`Embedding → Vector Index → Retriever`), Agent(`Tool API`) 확장 시에도 오늘 만든 앞뒤 안전장치를 코드 수정 없이 그대로 재사용할 수 있다.