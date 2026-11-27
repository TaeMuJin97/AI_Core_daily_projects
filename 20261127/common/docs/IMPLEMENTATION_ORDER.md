# Day30 구현 순서 · SRS v1.0 대응

서비스 뼈대부터 내부 구현을 연결하는 Top-down 흐름으로 개발합니다. `common/test/`를 프로젝트 루트로 복사한 후 `python -m test.NNN_test` 형식으로 해당 단계만 확인합니다. `test/README.md`의 옵션과 비용 조건을 따릅니다. 업무 구현 범위와 SRS는 유지하며 검증 파일은 정답을 포함하지 않습니다. 초기 미구현 Runtime은 과정용이며 완성 시 교체합니다. 상위 난이도는 별도 구현 계약을 따릅니다.

| 구현 절 | 파일과 핵심 작업 | 단계 확인 | SRS |
|---|---|---|---|
| 01 | 공통 설정, CUDA PyTorch 선행 준비 | 000, 001 | B-01~02 |
| 02 | main.py → Router → Schema·오류·Meter → 임시 Runtime | 002 (초기 서버 전용) | B-01·12·14 |
| 03 | 기존 DB·유효 ID 선택 | 003, 읽기 전용 SQL | B-03 |
| 04 | Settings·Connection·Repository·Preflight | 004, 005 | B-02·03·05·10 |
| 05 | Agent·Tool·Validator·Document·Retriever 인터페이스 → DB Runtime | 006 (직접/HTTP) | B-06·09~11·13 |
| 06 | 실제 E5·pgvector·Document | 007, 008 | B-04~06 |
| 07 | Cross-Encoder | 009 | B-07 |
| 08 | Runnable RAG·Context·Prompt | 010, 011 | B-08·13 |
| 09 | 최종 Runtime 연결 | 012, 선택 유료 013·014 | B-09~11 |
| 10 | 최종 FastAPI | 015 | B-12·14 |
| 11~14 | pytest·Live·Postman·DB Snapshot | tests/, scripts/, Postman, 016 | B-15 / T-01~10 |
| 상위 I | Query rewrite/expansion, 동일 후보 A/B, Gold 평가 | 별도 I-01~08 계약 | T-01~14 |
| 상위 A | DI·상한·graded nDCG·회귀·운영 보고 | 별도 A-01~08 계약 | T-01~19 |

## 인터페이스 계약 (강사용 참조 코드 기준)
- `Repository.candidates(vector, category_code, top_k, report_id=None)` → list[dict]. 필드 `report_id,title,content,overview,category_code,revision,distance`. 모든 필드는 실제 DB 조회값입니다.
- `Repository.lookup(report_id)` → found/not_found. `index_status,revision,embedding_fresh`는 DB에서 읽은 값입니다.
- `E5.encode(query,meter)` → float 384개. CUDA E5, query prefix, 정규화.
- `Retriever.search(query,category_code,top_k,meter,exact_ids=None)` → list[Document]. RPT-ID와 원문 Metadata.
- `Reranker.rank(query,docs,meter)` → 같은 후보 Document 목록. `reranker_score` 추가, 내림차순.
- `RagPipeline.retrieve(...)` → (ranked_docs, debug_info). `run(question,query,category_code,k,meter)` → RAG Tool Output Contract.
- `make_rag_tool(...)`, `make_db_tool(...)` → 등록할 `@tool` 객체. 모델이 인수를 제안하고 런타임이 실행합니다. `InjectedToolCallId`는 서버 주입 값으로 모델 Schema에 노출하지 않습니다.
- `AgentService.ask(request_id,request,meter)` → API 계약 dict. Tool selection을 if/elif로 고정하지 않습니다.
- `trace_from_messages(messages,ledger)` → (trace, 실제 결과). `finalize(...)` → AskResponse. 완료 검증용 키워드 규칙은 실행 라우터가 아닙니다. 명확한 상태/내용/복합 시나리오를 대상으로 하며 모든 자연어 업무 의도를 완벽하게 판정하지는 못합니다.

## SQL 핵심
기존 `reports`, `report_embeddings`, `report_read_view`를 같은 SELECT로 조회하여 벡터와 원문 Revision을 일관되게 읽습니다. `ready`, E5 모델, dimension, revision, UTF-8 SHA-256 일치를 확인합니다. 영벡터도 제외합니다. `:vec,:model,:cat,:rid,:k` 파라미터를 바인딩합니다. DB transaction은 READ ONLY. 기존 로그인 권한 자체가 제한됐다는 뜻은 아니므로 실제 운영에서는 전용 SELECT 계정을 별도로 설계해야 합니다(이번 신규 DDL은 금지).

## 코드 설계 보충
- RAG 내부 생성 LLM과 Agent 최종 LLM을 구분합니다. 매 요청의 모델 호출과 도구 호출 상한, 각 LLM timeout을 적용합니다. SDK 자동 retry=0; 429 등은 원인을 분리하고 수동 재시도 전에 비용을 확인합니다. GPU 모델 로딩은 별도 측정하며 전체 HTTP 요청의 강제 wall-clock 취소는 구현하지 않습니다.
- Tool의 실제 반환값과 AIMessage/ToolMessage ID, 서버 ledger를 대조합니다. 존재하는 출처가 문장의 사실성을 보장하지는 않으므로 사람 평가가 필요합니다.
- `RPT-63`처럼 명시 ID를 보호하는 검색 필터를 사용합니다. Query Rewrite는 원 질문을 후보에 반드시 유지합니다. 명시 ID/영문·수치 보존 규칙은 기계적 하한일 뿐 의미 보존 자체는 사람이 확인합니다. 안전한 대안이 없으면 원 검색 질문만 사용될 수 있습니다.
- Basic에서도 상한과 Pydantic 검증은 필수. Basic은 `ProviderStrategy(ModelAnswer)` 및 `result['structured_response']`를 사용합니다. 상위 단계는 명시적인 `args_schema`, `ProviderStrategy(StructuredModelAnswer)`와 실제 DB 조회의 `status_report_ids` 대조, A/B, 평가, Run Store 등을 추가합니다.
- Advanced Run Store는 프로세스 내 최대 100건의 요약만 보존하며 사용자 질문·원문·Key·DB URL은 저장하지 않습니다.
- `OUTPUT_CONTRACT_ERROR`(500), `CONFIG_INVALID`(503), `EXECUTION_LIMIT`(503), `NOT_IMPLEMENTED`(500)는 SRS 공통 Envelope 안에서 원인 구분을 위해 추가한 구현 코드입니다. 
- 이 자료는 LangChain 1.x / langchain-openai 1.x 호환 범위로 작성했습니다. 공식 문서: https://docs.langchain.com/oss/python/langchain/agents / https://docs.langchain.com/oss/python/langchain/tools / https://docs.langchain.com/oss/python/langchain/middleware/built-in / https://docs.langchain.com/oss/python/langchain/middleware/custom
- RAG 내부의 출력은 기존 Runnable + JSON 파싱을 유지합니다. 전체 요청 중 문서 내용만 완료 판단하며 상태 조회가 빠졌다고 RAG를 실패 처리하지 않습니다. Agent 전체 완료 여부는 `finalize`가 검증합니다.
- Agent의 `ProviderStrategy`는 네이티브 출력 지원 모델에서 사용합니다. `ToolStrategy`로 임의 전환하지 않습니다(출력용 Tool이 업무 Tool ledger와 충돌할 수 있음). 공급자 오류 및 잘못된 출력은 기존 실패 계약으로 처리합니다. 참고: https://docs.langchain.com/oss/python/langchain/structured-output
- `.env`의 테스트 ID를 DB 확인값으로 유지하고 `pytest.ini`와 `python -m pytest tests/ -q -ra`로 테스트 범위를 선택합니다.
