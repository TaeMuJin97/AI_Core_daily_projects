# Day 22. 프로덕션급 LLM API 클라이언트 설계 및 회고 (AI 지식 답변 생성기 v2)

## 1. 들어가며: 단순 SDK 호출(`responses.create`)과 'LLM Client'의 차이

처음 외부 LLM API를 연동할 때는 `openai` 패키지를 설치하고 API 키를 넣어 답변 텍스트 한 줄을 받아보는 것에 집중하기 쉽다. 하지만 실제 서비스 백엔드(FastAPI + PostgreSQL)에 LLM을 붙이려면 단순 SDK 호출만으로는 운영이 불가능하다. 네트워크는 언제든 끊길 수 있고, HTTP 200 응답이 와도 모델이 안전 정책상 답변을 거절(`refusal`)하거나 토큰 상한에 걸려 JSON이 반토막(`incomplete`) 날 수 있으며, 무분별한 재시도는 API 요금 폭탄으로 이어지기 때문이다.

어제(Day 21)가 모델 호출 앞뒤의 '입출력 데이터 계약과 로컬 검증기'를 설계한 과정이었다면, 오늘(Day 22)은 수동 응답 수집을 걷어내고 **인증·Structured Outputs·스트리밍·오류 분류·비용 정산·응답 캐시·모델 라우팅이 결합된 운영 수준의 LLM 클라이언트(v2)**를 완성한 과정이었다. 오늘 구축한 전체 아키텍처와 핵심 엔지니어링 결정들을 정리해 둔다.

---

## 2. 전체 클라이언트 파이프라인 아키텍처 (End-to-End 흐름)

```text
[질문(H01~H03) + 선택 지식(101~103) + 고정 Instructions]
   │
   ▼
[1. Model Routing (07)] ── 실행 모드(fast/quality) 검증 및 모델·선택 사유(route_reason) 확정
   │                       (미지원 모드는 조용한 fallback 없이 즉시 ValueError 차단)
   ▼
[2. Response Cache 조회 (06)] ── SHA-256 키(scope + model + request + format + validator_version)
   │  ├─ (Cache Hit: TTL 유효 + 사람 승인 + 현재 규칙 재검증 통과)
   │  │     └──► [즉시 반환] source_mode="app_cache", new_api_send_count=0, origin_run_id 보존
   │  └─ (Cache Miss: 미존재 / 만료 / 미승인 / 지식 본문 변경 등)
   ▼
[3. 요청 조립 및 전송 제어 (01, 02, 04)]
   │  ├── 역할 분리: instructions(규칙) vs input(직렬화된 question + knowledge)
   │  ├── Wire Schema: text.format = OUTPUT_FORMAT (서버 측 JSON 구조 강제)
   │  └── 2차원 전송 예산: 생성 최대 2회 × 생성당 전송 최대 2회 (총 전송 <= 4, 시간 예산 60s)
   │        ├─ 401(인증) / 403(권한) / 429(quota 소진) / Timeout ──► [즉시 중단 (Stop)]
   │        └─ 429(일시적 rate_limit) / 선별 5xx ──► [Retry-After 및 남은 예산 확인 후 대기·재전송]
   ▼
[4. 응답 수신 및 1차 관문: Response Gate (02, 03)]
   │  ├── Streaming(H01): 단조 시계(perf_counter)로 첫 텍스트 시간(first_text_ms, TTFT) 측정,
   │  │                   부분 조각(delta)과 공식 종료 이벤트(response.completed)의 최종 객체 분리
   │  └── Response Gate: 로컬 파싱 전 refusal(거절) · incomplete(미완료) · empty_output 사전 분리
   ▼
[5. 로컬 3단계 계약 검증 및 제한된 형식 수정 (Day 21 연결)]
   │  ├── strict JSON 문법 → KnowledgeAnswer(Pydantic strict=True) → check_rules(출처·상태 규칙)
   │  └── json_error / schema_error에 한해 최대 1회 형식 수정 생성(generation_no=2) 허용
   ▼
[6. 관측 기록 및 정밀 비용 정산 (05, 08)]
   │  ├── 토큰 분리: 일반 입력(input - cached), 캐시 입력(cached), 출력(output, 추론 포함)
   │  ├── Decimal 정산: 부동소수점 오차 없이 USD/1M 단가 적용 (미수신 usage는 0이 아닌 None 보존)
   │  └── 사람 근거 검토 대기(evidence_ok=None) → tools/review.py 승인 시에만 캐시 자격 부여
```

---

## 3. 모듈별 핵심 설계 포인트와 내가 이해한 원리

### Step 1. 환경변수 분리와 과금 안전장치 (`01_first_call`, `coursekit/support.py`)

- `.env`와 `!.env.example` 패턴
  - 실제 `OPENAI_API_KEY`가 들어있는 `.env`는 `.gitignore`로 차단하고, 변수명만 적힌 `.env.example`만 예외 허용(`!`)으로 Git에 공유했다. 또한 응답 요약 뷰(`connection_view.json`)나 로그에도 API 키는 절대 남기지 않고 `source_mode`, `model`, `run_status`, `response_id`만 기록한다.
- AST 정적 검사와 이중 잠금 스위치
  - `support.py`의 `ensure_completed`가 실행 전 파이썬 `ast` 모듈로 소스 코드를 스캔해 미완성 `NotImplementedError`가 남아 있으면 API 호출 자체를 차단한다. 또한 실제 과금이 발생하는 호출은 반드시 `--source live --allow-paid`를 명시해야만 열리도록 설계되어 실수로 인한 크레딧 소모를 방어한다.

### Step 2. 이중 스키마(`WireAnswer` vs `KnowledgeAnswer`)와 `response_gate` (`02_structured_output`)

- 왜 서버 측 Structured Outputs를 쓰는데도 로컬 Pydantic 검증을 유지하는가?
  - Responses API의 `request["text"] = {"format": OUTPUT_FORMAT}`에 전달하는 `WireAnswer`는 모델이 4개 필수 필드와 기본 자료형을 갖춘 JSON을 생성하도록 돕는 전송 경계(Wire)의 약속이다.
  - 하지만 서버 스키마는 모델이 `source_ids`에 이번 요청에 주지 않은 ID(`999`)를 적었는지, `insufficient_context`인데 안내문 규칙을 어겼는지까지는 막아주지 못한다. 따라서 서버 측 `WireAnswer`와 로컬의 엄격한 `KnowledgeAnswer` + `check_rules`를 이중으로 결합해야 한다.
- 세 가지 계층의 `status` 구분 (`response_gate`)
  - 통신 성공(`HTTP 200`), 모델 생성 완료(`response.status == "completed"`), 비즈니스 답변 가능 여부(`answer_object.status == "answered"`)는 완전히 다른 계층의 상태다.
  - 만약 모델이 안전 정책으로 거절(`type == "refusal"`)했거나 토큰 상한에 걸려 미완료(`incomplete`)된 응답을 곧바로 JSON 파서에 넣으면 `json_error`로 오판해 불필요한 형식 수정 재시도(API 요금 낭비)를 하게 된다. 이를 막기 위해 `response_gate`가 로컬 검증기 앞에서 거절·미완료·빈 출력을 먼저 걸러낸다.

### Step 3. 스트리밍 수신과 TTFT(`first_text_ms`) 및 완료 판정 (`03_streaming`)

- 체감 지연 시간(TTFT)과 단조 시계
  - 전체 생성 완료 시간(`e2e_ms`)이 같더라도 첫 글자가 찍히는 시간(`first_text_ms`)이 빠르면 사용자의 체감 대기 시간은 크게 줄어든다. 이때 시스템 시계 동기화에 흔들리지 않는 `time.perf_counter()` 단조 시계를 사용하며, 빈 문자열(`delta == ""`)은 첫 표시로 세지 않는다.
- 부분 미리보기(`parts`)와 최종 응답(`final`)의 분리
  - SSE 스트리밍으로 도착하는 `delta` 조각의 개수는 과금 기준인 토큰 수(`usage`)와 다르다.
  - 또한 부분 문자열을 합쳤다고 해서 클라이언트가 임의로 완료(`completed`) 판정을 내리거나 부분 JSON으로 DB 변경·도구 실행을 하면 안 된다. 오직 서버가 보낸 종료 이벤트(`response.completed` 등)의 `event.response` 객체만을 최종 상태로 보관해 검증기로 넘기고, 그 안의 공식 `usage`를 읽어야 한다.

### Step 4. 같은 HTTP 429의 분기와 2차원 재시도 예산 (`04_error_handling`)

- SDK 자동 재시도 비활성화 (`max_retries=0`)
  - SDK 내부 재시도와 애플리케이션의 형식 수정 재시도가 겹치면 호출 횟수가 `2 × 2 × (SDK 재시도)`로 증폭되고 실패 이력이 숨겨진다. 따라서 SDK 재시도는 `0`으로 끄고 앱에서 모든 전송을 통제한다.
- 기다릴 오류 vs 즉시 멈출 오류
  - `401`(인증), `403`(권한)은 기다려도 키가 바뀌지 않으므로 즉시 중단한다.
  - 특히 같은 `429`라도 에러 코드가 `insufficient_quota`(크레딧 소진)이면 즉시 중단(`retryable=False`)하고, `rate_limit_exceeded`(일시적 RPM/TPM 제한)일 때만 `Retry-After` 최소 대기 시간과 남은 시간 예산(`remaining_s`)을 비교해 재전송한다. 필요한 대기 시간이 남은 예산보다 길면 대기 시간을 억지로 줄이지 않고 `None`(`deferred`)을 반환해 즉시 포기한다.
- 2차원 예산 (`2 × 2 = 4`)
  - 생성 시도(`max_generations=2`: 최초 생성 + 형식 수정 1회)와 각 생성 내 통신 재전송(`max_sends_per_generation=2`)을 분리하되, 전체 누적 전송 상한을 `max_sends_total=4`로 제한했다.

### Step 5. 토큰 포함 관계와 `Decimal` 기반 정밀 비용 계산 (`05_usage_cost`)

- 이중 과금 방지를 위한 토큰 분리 산식
  - API가 반환하는 `input_tokens` 안에는 이미 할인 단가가 적용되는 `cached_tokens`가 포함되어 있다. 따라서 일반 입력 단가는 반드시 `uncached = input_tokens - cached_tokens`에만 곱해야 한다. 마찬가지로 `output_tokens` 안에는 이미 `reasoning_tokens`가 포함되어 있으므로 출력 비용에 다시 더하지 않는다.
- `Decimal` 연산과 `None`(미관측) 보존
  - 100만 토큰당 달러(`USD / 1M Tokens`) 단가 계산 시 이진 부동소수점(`float`) 오차를 막기 위해 `decimal.Decimal`을 사용했다.
  - 타임아웃 등으로 `usage`를 받지 못했을 때 `or 0`으로 채우면 미확인 비용이 '0원 무료 호출'로 둔갑하므로, 관측하지 못한 값은 `None`(`estimated_usd=None`)으로 남겨 알려진 비용 소계와 미확인 전송 건수를 분리해 기록한다.

### Step 6. 사람 승인 기반 Response Cache와 6중 무결성 검증 (`06_response_cache`)

- 세 가지 캐시의 구분
  - 모델 내부의 `KV Cache`나 공급자 서버가 입력 앞부분 연산만 재사용하는 `Prompt Caching`(`cached_tokens`)과 달리, 우리가 구현한 앱의 `Response Cache`(`app_cache`)는 최종 답변 자체를 재사용해 신규 API 전송을 `0회`로 만든다.
- SHA-256 캐시 키(`key_of`)와 읽기 시점 재검증(`checkpoint_cache`)
  - 질문 문자열만 같다고 같은 답을 주면 안 된다. `scope`(권한 범위), `model`, `request`(질문 + 선택 지식 원문 전체), `format`(Schema), `validator_version`을 모두 정렬해 SHA-256 해시 키를 만든다. 덕분에 지식 ID(`103`)가 같아도 본문(`content`)이 한 줄이라도 바뀌면 해시 키가 즉시 달라져 예전 캐시가 무효화된다.
  - 캐시를 읽을 때도 ① 키 일치, ② TTL 유효기간, ③ 사람의 근거 검토 승인(`review.json`), ④ 권한 및 출처(`api_live` vs `simulated`) 일치, ⑤ 현재 문맥(`provided_ids`) 기준 로컬 검증기 재통과 여부를 모두 확인한 뒤에만 재사용하며, `origin_run_id`로 최초 생성 이력을 추적한다.

### Step 7. 명시적 모델 라우팅과 회귀 통합 검증 (`07_model_routing`, `08_daily_project`)

- 호출 전 선택(`route`)과 공통 결과 계약(`record_view`)
  - `fast`(`gpt-5.4-mini-2026-03-17`)와 `quality`(`gpt-5.4-2026-03-05`) 중 허용된 모드만 통과시키고 `route_reason`을 기록한다. 어떤 모델을 쓰든 동일한 10개 필드로 결과를 남기며, 소수 관찰만으로 고가 모델이 무조건 우월하다고 단정하지 않는다.
- `H01~H03` 배치 실행 및 서킷 브레이커 (`daily_project`)
  - `H01`(스트리밍), `H02`(정보 부족), `H03`(다중 근거 요약)을 연속 실행해 `observations.csv`와 `summary.json`을 생성하고, `check_project`를 통해 사람 미평가 상태(`evidence_ok is None`)와 전송 상한(`new_api_send_count <= 4`)을 최종 검증했다.

---

## 4. 주요 실행 및 검증 명령어 요약

```bash
# 1. 8교시 AI 지식 답변 생성기 v2 배치 실행 (H01 스트리밍 + H02~H03 호출)
python main.py --source live --allow-paid

# 2. 생성된 응답에 대한 사람의 근거 대조 승인 기록 (tools/review.py)
python ../../tools/review.py --run-file "<생성된_run.json_경로>" --decision approve --note "원문 근거 대조 완료"

# 3. 승인된 답변의 앱 캐시 재사용(Cache Hit, 신규 전송 0회) 및 문맥 변경 미스(Cache Miss) 확인
python main.py --source live --action reuse --run-file "<승인된_run.json_경로>"
python main.py --source live --action changed --allow-paid --run-file "<승인된_run.json_경로>"
```

---

## 5. 다음 단계 연결 (Day 23~ RAG & Agent)

오늘까지 구축한 `LLM Client`(입력 조립 → 모델 라우팅 → 캐시 조회 → 제한된 전송·스트리밍 → 응답 게이트 → 로컬 계약 검증 → 비용·시간·출처 기록)는 데이터 소스가 어디든 그대로 재사용할 수 있는 독립 모듈이다. 내일 이어질 `Embedding → Vector Index → Retriever` 기반의 RAG 파이프라인에서는 지금까지 사람이 수동으로 골라주던 지식 스냅샷(`101~103`) 선택 단계만 검색기로 자동화하여 오늘 만든 클라이언트 앞단에 연결하게 된다.