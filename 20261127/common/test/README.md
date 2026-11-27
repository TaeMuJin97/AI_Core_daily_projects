# Day30 단계별 실행 검증 (공통 제공)

`common/test/`는 강사·수강생이 함께 사용하는 개발 중간 검증 코드이며 업무 구현 정답이 아닙니다. 프로젝트 루트에 `test/`로 복사하고, VS Code에서 해당 프로젝트를 열어 실행합니다. 파일을 직접 타이핑하지 않습니다. `tests/`(pytest 계약·회귀 검사), `scripts/verify_live.py`(통합 Live), Postman은 별도로 유지합니다. 아래 검증은 Basic의 참조 인터페이스 및 현업형 Top-down 순서 기준입니다. 상위 난이도는 공통 API/인터페이스를 구현한 뒤 필요한 검증을 사용하며 다른 구조를 설계했다면 검증 어댑터만 수정합니다. 초기 뼈대 002는 미구현 Runtime을 쓰는 단계 전용입니다.

```bash
# 예: 새 빈 프로젝트 루트에서 실행. 실제 common 경로로 변경
PREP="../Day30_20261127_pjt/common"
cp -rn "$PREP/test" .
cp -n "$PREP/pytest.ini" .
# 이미 있는 test/가 있다면 원본과 대조하고 필요한 파일만 갱신
nvidia-smi
python -m test.000_test
```

`python -m test.000_test`부터 필요한 번호만 실행합니다. 000 통과 후 `python -m pip install -r requirements.txt`, `python -m pip check`, 001을 수행합니다. 모든 파일을 한꺼번에 실행하지 않습니다. `python -m pytest tests/ -q -ra`는 `test/`를 수집하지 않습니다. 프로젝트 루트에서 `python -m`으로 실행해야 `app`과 `test`를 일관되게 찾습니다. `[PASS]`와 종료 코드 0은 해당 검증만 통과했음을 의미합니다. 로그/AssertionError를 확인하고 구현을 수정한 뒤 같은 파일을 재실행합니다.

| 번호 | 단계 | 검증 내용 | 실행 | 비용 |
|---|---|---|---|---|
| 000 | 01 | 설치 전 CUDA 확인 | `python -m test.000_test` | LLM 미호출(기본) |
| 001 | 01 | 패키지·GPU 실제 연산 | `python -m test.001_test` | LLM 미호출(기본) |
| 002 | 02 | 최초 API 뼈대 | `python -m test.002_test` | LLM 미호출(기본) |
| 003 | 03 | 환경변수·테스트 ID | `python -m test.003_test` | LLM 미호출(기본) |
| 004 | 04 | DB·GPU Preflight | `python -m test.004_test` | LLM 미호출(기본) |
| 005 | 04 | 시작 DB Snapshot | `python -m test.005_test` | LLM 미호출(기본) |
| 006 | 05 | DB Tool·중간 Runtime | `python -m test.006_test` | LLM 미호출(기본) |
| 007 | 06 | E5 Embedding | `python -m test.007_test` | LLM 미호출(기본) |
| 008 | 06 | pgvector·원문 Metadata | `python -m test.008_test` | LLM 미호출(기본) |
| 009 | 07 | Cross-Encoder Reranking | `python -m test.009_test` | LLM 미호출(기본) |
| 010 | 08 | Context·Prompt | `python -m test.010_test` | LLM 미호출(기본) |
| 011 | 08 | 출처 Validator (Fixture) | `python -m test.011_test` | LLM 미호출(기본) |
| 012 | 09 | 최종 Runtime 조립 | `python -m test.012_test` | LLM 미호출(기본) |
| 013 | 09 | RAG Tool 직접 실행 | `python -m test.013_test --allow-paid-llm` | 유료(명시 동의) |
| 014 | 09 | Agent 복합 요청 | `python -m test.014_test --allow-paid-llm` | 유료(명시 동의) |
| 015 | 10 | 최종 HTTP API | `python -m test.015_test` | LLM 미호출(기본) |
| 016 | 14 | DB 불변성 | `python -m test.016_test` | LLM 미호출(기본) |

## 실행 조건과 선택 옵션

- 002: `--imports-only`로 서버 실행 전 OpenAPI 검사, `python -m app.main`으로 초기 임시 Runtime 서버 실행 후 다른 터미널에서 기본 명령으로 /docs, /health 500, 422, 정상 형식 요청 500 확인. 완성된 서버에는 002를 실행하지 않습니다. 기존 서버는 Ctrl+C로 종료합니다.
- 003: `.env`의 실제 두 ID를 읽습니다. 기존 export 값은 우선하므로 필요하면 `unset DAY30_REPORT_ID DAY30_MISSING_ID` 후 다시 실행합니다. DB에서 ID가 실제로 존재/부재하는지는 004에서 검증합니다.
- 005: 시작 시 한 번만 수행합니다. 기준 파일이 이미 존재하면 실패하며, 새 점검을 시작하는 경우에만 `--replace-baseline`을 명시합니다. 진행 중 기준선을 바꾸지 않습니다.
- 006: 기본은 DB Tool 직접 호출; `--imports-only`는 Agent/Runtime import 검사; 서버 실행 후 `--http`는 /health, 422 확인; 선택적으로 `--http --allow-paid-llm`은 실제 DB 단독 Agent 요청 1건(유료, 모델 호출 횟수는 달라질 수 있음).
- 013/014: `--allow-paid-llm` 없이는 실행하지 않습니다. 12절의 Live 테스트와 중복 비용이 발생하므로 선택입니다.
- 015: `--imports-only`는 최종 서버 실행 전 검사, 기본은 실제 HTTP /docs, /health, 422. `--allow-paid-llm`은 선택 복합 질문 1건(유료). Postman 전체 검증은 별도입니다.
- 016: 최초 `outputs/db_before.json`과 현재 DB를 비교하고 `db_after.json`을 기록합니다. 변경 발견 시 실패합니다. DB를 복구·수정하지 않습니다.
- 무료라는 표현은 외부 LLM 미호출을 뜻합니다. Hugging Face 다운로드와 CUDA 연산은 실제 수행될 수 있습니다. 콘솔 답변/원문은 로컬 확인 전용이며 비밀과 원문을 제출하지 않습니다. 테스트 013/014/015의 실제 답변 내용은 DB 원문과 사람이 대조합니다.
