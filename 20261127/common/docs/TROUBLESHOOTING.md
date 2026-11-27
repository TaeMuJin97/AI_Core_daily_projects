# 오류 대응 · 먼저 실제 원인을 확인하세요
| 증상 | 확인 | 조치 |
|---|---|---|
| `ModuleNotFoundError` | `python -m test.000_test` | 기존 정상 CUDA venv 선택, pip install -r requirements.txt, pip check |
| `DB_UNAVAILABLE` | pgAdmin에서 DB명, table/view, pgvector, 접속 URL 확인 | 기존 DB 선택·접속 정보 수정. CREATE/seed 실행 금지 |
| `EMBEDDING_UNAVAILABLE / no_eligible_vectors` | 읽기 전용 SQL의 유효 ready 벡터 수 | 11/20 인덱싱 준비를 강사와 확인. Day30 코드로 변경 금지 |
| `GPU_UNAVAILABLE` | `nvidia-smi`, `torch.__version__`, `torch.version.cuda`, `torch.cuda.is_available()` | `+cpu`/None이면 CUDA 빌드 설치. RTX 5080 확인 사례는 cu130. 공통 시작 안내의 설치 전후 점검 수행, CPU fallback 금지 |
| `KeyError: DAY30_REPORT_ID` | `.env`, 현재 터미널 export 값 | 실제 ID를 `.env`에 저장하고 load_settings 이후 읽기. CLI 인자를 생략하거나 확인한 숫자 사용 |
| pytest `import file mismatch` / `app.evaluation` / `app.services.run_store` | 프로젝트 루트 `pytest.ini`와 테스트 경로 | `python -m pytest tests/ -q -ra`. common/tests 전체 수집 금지, 상위 단계 파일을 억지로 구현하지 않음 |
| HF Hub 비인증 Warning | 모델 로딩 완료 여부 | 공개 모델이 정상 로딩되고 추론 성공하면 오류 아님. 다운로드 제한 시 인증/캐시 확인 |
| `RERANKER_UNAVAILABLE / gpu_oom` | VRAM 및 실행 중인 프로세스 | 불필요한 GPU 작업 종료, `.env`의 RERANK_BATCH_SIZE를 1로 감소. 모델 변경은 명세 변경 |
| 모델 로딩 실패 | Hugging Face 모델 캐시·네트워크·파일 상태 | 실제 모델 두 개를 미리 준비; 재설치는 강사 확인 후 |
| `LLM_UNAVAILABLE / authentication` | 실제 키·모델 ID·endpoint | 키가 존재하는 것과 유효한 것은 다름. 원본 키나 예외 출력 금지 |
| `LLM_UNAVAILABLE / rate_limit` | 사용량·요금·429 | 과도한 자동 재시도 금지. 호출 예산·공급자 제한 확인 |
| `LLM_TIMEOUT` | 요청 timeout / 서버 지연 | 상한 범위에서 설정 조정, 동일 호출 무한 반복 금지 |
| `OUTPUT_CONTRACT_ERROR / rag_status_rule` | RAG 내부 상태와 source_ids의 조합 | RAG는 문서 내용만 완료 판단. `completed`는 실제 출처 필수, `insufficient_evidence`는 출처 없음, `incomplete` 금지. Validator 유지 |
| `OUTPUT_CONTRACT_ERROR / invalid_model_json` | RAG 내부 JSON 형식/필드 | RAG의 Prompt와 Pydantic 계약 점검. 잘못된 출력을 성공으로 처리하지 않음 |
| `OUTPUT_CONTRACT_ERROR / invalid_structured_response` 또는 Provider 오류 | Agent 모델의 Tool Calling + 네이티브 Structured Output 지원 여부 | `ProviderStrategy`와 `structured_response`를 사용. ToolStrategy를 임의 사용하거나 마지막 메시지 content를 재파싱하지 않음. 출처/ledger 검사 유지 |
| `EXECUTION_LIMIT` | Tool/Model 호출 수, 복합 질문 | 상한은 서버 정책. 무한 반복 금지 |
| `NOT_IMPLEMENTED` | 해당 B-ID TODO | 지정 함수부터 구현. 강사 가이드 및 테스트 참조 |
| `incomplete` | 필요한 두 Tool 중 누락/잘못된 결과 | AIMessage와 실제 ToolMessage 대조. 단순 200을 성공으로 보지 않음 |
| `insufficient_evidence` | 실제 유효 근거가 없거나 미존재 | 관련 없는 검색 1위를 억지 정답으로 만들지 않음 |
| 404 `/rag/debug` 또는 `/agent/runs` | 선택한 난이도 | 각각 Intermediate/Advanced에서만 제공 |
| Port 8000 사용 중 | 기존 11/20 서버/다른 uvicorn | 기존 서버 종료 또는 다른 로컬 포트로 실행, Postman base_url 일치 |

**실제 환경 확인:** 설치 전/후 `python -m pip freeze > outputs/environment_versions.txt`는 필요 시 실행합니다. .env/Key/DB URL, 원본 오류 trace, 전체 Context, DB dump를 제출하지 마세요. `LLM configured`는 실제 인증 성공의 증거가 아닙니다.

## 단계별 검증
`No module named test`가 발생하면 프로젝트 루트에 `common/test/`를 복사했는지 확인하고 `python -m test.000_test`처럼 실행하세요. 002는 초기 임시 Runtime 전용입니다. 013/014는 `--allow-paid-llm` 없이는 실행하지 않습니다. 005에서 기존 Snapshot 때문에 중단되면 기존 기준을 보존하며, 새 점검에 한해 `--replace-baseline`을 사용합니다.
