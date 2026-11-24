# 실행 기록 (직접 작성)

- 선택 단계 / 실습: `01_basic` / `01_failure_diagnosis` (검색 실패 위치 진단)
- 실행 날짜와 Python Interpreter: 2026-11-24 / Python 3.13 (`C:\workspace\envs\.backendenv`)
- 실행 모드: **offline_fixture** (`execution_mode: "fixed_diagnostic_cases"`, 실제 DB·Embedding·LLM 모델 미실행, `outputs/day27_01_fixture.json`)
- 요청 질문과 Category: 해당 없음 (실제 검색 질의 대신 `coursekit.workshops.CASES`의 고정 진단 사례 `F01`~`F07` 상태 플래그 입력 사용)
- Query Rewrite의 원 질문과 검색용 질문: 해당 없음 (실제 Rewrite 모델 호출 미실행; 진단 사례 `F01`에서 `ambiguous: True` 조건을 통해 `Query Rewrite`가 필요한 단계임을 판별함)
- Candidate ID → Rerank ID → Context included ID: 해당 없음 (실제 청크 ID 검색 대신 `gold_in_candidates`·`gold_in_context`·`valid_source` 조건으로 단계별 실패 위치를 진단함 — `F02` 후보 누락 → `Candidate Retrieval`, `F03` 후보 포함·Context 탈락 → `Reranking`, `F04` Context 포함·출처 무효 → `Validation / Citation`, `F05` 전 단계 통과 → `No Failure (Healthy)`)
- 답변과 출처 문서의 실제 내용 대조: 실제 LLM 생성 답변이나 DB 조회가 없는 고정 진단 실습이므로 문장 단위 Grounding 대조 대상은 없음. 대신 생성된 `outputs/day27_01_fixture.json`의 7개 사례(`F01`~`F07`) 진단 결과가 강의 15페이지의 실패 분류 기준(`F06` `authorized: False` → `Authorization / Access Filter`, `F07` `current: False` → `Version / Metadata Filter` 포함)과 일치함을 확인함
- 실패 또는 예상과 다른 결과: `python -m pytest -q tests` 실행 시 기능 검증(`test_offline_contract`)은 `1 passed`로 정상 통과했으나, Windows 기본 콘솔 인코딩(`cp949`) 출력과 `pytest`의 `utf-8` 서브프로세스 읽기 간 충돌로 `UnicodeDecodeError` 스레드 경고(`1 warning`) 1건이 발생함 (`PYTHONUTF8=1` 환경변수로 해결 가능)
- 고친 TODO와 이유:
  - `D27-01-B01` (`diagnose_stage`): RAG 파이프라인 처리 순서(`질문 모호성 → 접근 권한 → 최신·준비 버전 → 1차 후보 포함 → 2차 Context 포함 → 출처·형식 검증`)대로 위에서부터 조건을 검사해 가장 먼저 발생한 근본 원인 단계를 반환하도록 구현함
  - `D27-01-B02` (`recommend_action`): 진단된 단계에 맞는 개선 처방을 반환하며, 특히 `Candidate Retrieval`(후보 누락) 단계에서는 Reranker가 후보 밖 문서를 되살릴 수 없으므로 검색 범위·`candidate_k`·Query Expansion/Multi-query·인덱싱을 점검하도록 명시함
- 다음 개선 가설 (실측 전에 성공으로 단정하지 말 것): `F01`처럼 대상이 생략된 후속 질문(`ambiguous: True`)의 경우, 다음 실습(`02_query_rewrite`)에서 대화 `History`를 바탕으로 원래 질문을 보존한 채 독립 질문(`Standalone Query`)으로 재작성하면 검색 전 질문 모호성으로 인한 실패를 줄일 수 있을 것으로 예상됨 (단, 실제 효과는 후속 실습 실행 결과로 확인 필요)