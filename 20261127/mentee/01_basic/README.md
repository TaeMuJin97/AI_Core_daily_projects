# Day30 · 01_basic 수강생용

**목표:** 비전공자도 이번 신규 프로젝트에서 실제 LangChain Agent + Tool 2개를 구현합니다. 제공한 코드는 환경, 예외, 데이터 모델, 호출 예산, 실행 도우미 등 공통 골격이며 아래 TODO는 직접 완성해야 합니다. 11/20 Python 코드 재사용 금지, 기존 DB만 조회.

## 실행 전에
`../../common/README_START.md`와 `../../common/docs/Day30_SRS_v1.0.html`을 읽으세요. 기존 CUDA venv를 사용하고 `.env.example`을 `.env`로 복사하여 실제 값 입력. `python -m pip install -r requirements.txt`, `python -m pip check`. 현재 골격은 일부 기능이 NOT_IMPLEMENTED인 것이 정상입니다.

## TODO 순서
| 순서 | ID | 파일 | 구현 목표 |
|---|---|---|---|
| 1 | B-02 | `app/core/preflight.py` | repo.preflight()와 require_cuda()의 결과를 얻으세요. 유효 벡터 0 및 키/모델 미설정은 ServiceError. 상태 dict에 gpu, embedding_model, reranker_model, llm=configured 등을 담아 반환하세요. |
| 2 | B-04 | `app/rag/embeddings.py` | self.model.encode에 query: 접두어가 붙은 문자열을 전달하고 normalize_embeddings=True를 지정하세요. ndarray를 list로 변환하세요. |
| 3 | B-05 | `app/db/repository.py` | SELECT에 VIEW 필드와 embedding cosine distance(<=>)를 포함하세요. 고정 JOIN/FRESH를 사용하고 :vec, :cat, :rid, :k, :model 바인딩을 적용해 distance 오름차순 TOP-k를 반환하세요. SQL 문자열에 사용자 입력을 직접 넣지 마세요. |
| 4 | B-06 | `app/rag/documents.py` | Document의 page_content에는 row[content]를, metadata에는 source_id=RPT-번호, report_id/title/category_code/revision/overview/distance를 넣으세요. |
| 5 | B-07 | `app/rag/reranker.py` | (query, title + overview) 쌍 목록을 만들고 self.model.predict(..., batch_size=..., show_progress_bar=False)를 호출하세요. docs와 scores를 zip하여 점수 내림차순, ID 오름차순으로 ranked를 구성하세요. |
| 6 | B-08 | `app/rag/pipeline.py` | RunnableLambda에서 prepared의 question/query/context를 추출한 뒤 | RAG_PROMPT | model로 연결하세요. chain.invoke(prepared)의 AIMessage를 message에 저장하세요. |
| 7 | B-09 | `app/tools/rag_tool.py` | pipeline.run에 question, query, effective_category, args.k, meter를 순서대로 전달하세요. check_tool_output으로 rag_search 반환값을 검사하세요. |
| 8 | B-10 | `app/db/repository.py` | reports와 report_categories JOIN, report_embeddings LEFT JOIN을 사용하세요. WHERE report_id=:rid, FRESH의 COALESCE(false)로 최신성 검사. 실제 행이면 found, 없으면 not_found 반환. |
| 9 | B-11 | `app/agent.py` | create_agent에 model, tools, system_prompt, middleware를 전달하고 response_format=ProviderStrategy(ModelAnswer)를 지정하세요. agent.invoke의 messages에 user question과 Category를 넣고 config recursion_limit을 유한하게 지정하세요. |
| 10 | B-13 | `app/services/validator.py` | answer.answer에서 RPT-숫자 정규식으로 inline ID를 추출하세요. source_ids와 일치하고 중복이 없어야 하며 allowed 집합의 부분집합이어야 합니다. |
| 11 | B-12 | `app/api/agent.py` | runtime.agent.ask(request_id, body, meter)를 호출하여 반환하세요. 응답 형식은 AskResponse입니다. |

B-01·B-03·B-14는 제공 코드를 읽고 직접 설명/검증합니다. B-15는 실제 실행과 검증을 본인이 수행해야 합니다. TODO의 `raise ServiceError('NOT_IMPLEMENTED',...)`를 제거하고 해당 블록을 채우세요. 각 TODO는 한 가지 책임을 가진 함수에 있습니다.

## 단계별 실행
- Phase 01: B-02 완료 → `python -m scripts.preflight`. DB/GPU/LLM 설정을 확인합니다.
- Phase 02: B-04~07 및 B-10 완료 → `python -m scripts.verify_live` (무료, 모델 다운로드 필요). 실제 DB lookup 및 Reranking 확인.
- Phase 03: B-08~11, B-13 및 B-12 완료 → `python -m pytest tests/ -q -ra`. Fixture는 실제 모델 결과와 다릅니다.
- Phase 04: `python -m app.main` 실행 후 /docs와 Common Postman 사용. 실제 유료 실행은 동의 시 `python -m scripts.verify_live --allow-paid-llm`.
- Phase 05: `outputs/live_checks.json`, Postman, SQL 검증 결과 및 `common/docs/acceptance_checklist.csv` 기록. T-01~10 모두 확인하고 미실행/실패도 기록하세요.

## 주의
API-00, API-01만 이번 Basic 범위입니다. 무관 질문에 실제 근거가 없으면 `insufficient_evidence`; 복합 질문의 결과 누락은 `incomplete`. DB를 수정하지 않습니다. `RPT-63`은 실제 DB에서 확인해야 할 보고서 번호 예시입니다. CPU나 Fixture로 대체해 Live 성공으로 기록하지 않습니다.

## 실환경 점검 반영 사항
- CUDA torch가 먼저 설치되어야 합니다. CPU 전용 torch 문제는 `../../common/README_START.md`의 GPU 준비 절차를 따릅니다. 기존 정상 환경은 유지합니다.
- `.env`의 DAY30_REPORT_ID/DAY30_MISSING_ID는 실제 DB 확인값으로 수정합니다. `verify_live`는 CLI 인자 생략 시 이 값을 사용합니다.
- RAG의 completed는 문서 내용 업무 기준입니다. Agent 최종 응답은 ProviderStrategy 및 structured_response로 검증합니다. 모델은 Tool Calling과 네이티브 Structured Output을 동시에 지원해야 합니다.
- pytest는 이 프로젝트의 `tests/`만 실행합니다. 공통 참조 테스트 전체를 함께 수집하지 마세요.
