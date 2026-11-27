# Day30 · ADVANCED 강사용 정답 프로젝트

신규 독립 코드이며 11/20의 `report_agent_lab` DB만 읽기 전용 사용합니다. SRS v1.0, `common/README_START.md`를 먼저 확인하세요. 이 폴더를 VS Code로 열고 기존 CUDA venv에서 실행하세요. Basic의 `# BEGIN B-xx` ~ `# END B-xx` 주석은 수강생 TODO에 일대일 대응합니다.

```bash
python -m pip install -r requirements.txt
python -m pip check
if [ ! -e .env ]; then cp .env.example .env; fi
# .env에 기존 DB 연결과 실제 API 키/모델 입력
python -m pytest tests/ -q -ra
python -m scripts.preflight
python -m app.main
```

- `/health`: DB/GPU/설정 점검; LLM 실호출 성공은 별도.
- `POST /api/v1/agent/ask`: question, category_code. Swagger `http://127.0.0.1:8000/docs` 또는 Common Postman.
- `python -m scripts.verify_live`: 실제 CUDA/DB 및 lookup Tool 점검 (무료).
- `python -m scripts.verify_live --allow-paid-llm`: 실제 RAG와 Agent Loop의 단독/복합/no-answer 검사 (유료).

- `/api/v1/rag/debug`: Rewrite/Multi-query 및 동일 후보 Rerank A/B. 유료 Rewrite 발생.
- `python -m app.evaluation.retrieval_eval --k 3 --allow-paid-llm --generation`: Gold 고정 평가 및 사람 검토용 리포트. `--generation` 생략 가능.
- `/api/v1/agent/runs/{request_id}`: 실제 Run 요약, 최대 100개, 비영속. nDCG 및 운영 보고서 작성.

## 완료 기준
T-01~T-19. `common/docs/acceptance_checklist.csv`에 증거를 남기세요. 수강생 DB 상태가 달라진 경우 원본 Gold 또는 보고서 ID를 강제로 수정하지 마세요.

**현재 제작 검수와 교실 실행은 별개입니다.** 일부 프레임워크 테스트 및 Live GPU/DB/LLM 검증은 교실에서 수행해야 합니다. `outputs/README.md` 및 `common/docs/IMPLEMENTATION_ORDER.md` 참조.

## 실환경 점검 반영 사항
- CUDA torch가 먼저 설치되어야 합니다. CPU 전용 torch 문제는 `../../common/README_START.md`의 GPU 준비 절차를 따릅니다. 기존 정상 환경은 유지합니다.
- `.env`의 DAY30_REPORT_ID/DAY30_MISSING_ID는 실제 DB 확인값으로 수정합니다. `verify_live`는 CLI 인자 생략 시 이 값을 사용합니다.
- RAG의 completed는 문서 내용 업무 기준입니다. Agent 최종 응답은 ProviderStrategy 및 structured_response로 검증합니다. 모델은 Tool Calling과 네이티브 Structured Output을 동시에 지원해야 합니다.
- pytest는 이 프로젝트의 `tests/`만 실행합니다. 공통 참조 테스트 전체를 함께 수집하지 마세요.
