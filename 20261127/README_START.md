# Day30 · 2026-11-27 · LangChain AI Technical Report Agent

## 0. 가장 먼저 읽을 문서
`common/docs/Day30_SRS_v1.0.html`이 요구사항 기준입니다. 기존 11/20의 Python 프로젝트를 복사하거나 Import하지 않습니다. **기존 report_agent_lab DB만 읽기 전용으로 재사용**합니다. 이번 프로젝트에는 schema.sql, seed.sql, index_overviews.py가 없습니다. 신규 DB/테이블/벡터 생성은 금지입니다.

## 1. 난이도 선택 (하나만)
| 대상 | 시작 상태 | 완료 목표 |
|---|---|---|
| mentee/01_basic | 프로젝트 Skeleton, TODO, 테스트, README | B-01~15 / T-01~10 |
| mentee/02_intermediate | 폴더 구조만 | B + I-01~08 / T-01~14 |
| mentee/03_advanced | 빈 폴더 | B + I + A-01~08 / T-01~19 |
| mentor/ | 단계별 독립 정답 프로젝트 | 수강생에게 정답 ZIP 미배포 |

## 2. 공통 준비 (Windows 11 · VS Code · Git Bash)
1. 압축을 풀고 선택한 단계의 프로젝트 폴더를 VS Code에서 엽니다. **프로젝트 루트**에서 명령을 실행하세요 (`app/` 내부가 아님).
2. 기존 정상 CUDA PyTorch 가상환경을 선택/활성화합니다. `python -c "import sys; print(sys.executable)"`, `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"`로 인터프리터와 CUDA를 확인하세요.
3. 응용/심화는 아래 공통 파일을 선택한 프로젝트 루트에 복사합니다. Basic/강사용은 환경 템플릿과 requirements가 이미 있습니다. `common/prepare_project.py`는 선택한 프로젝트 폴더에 공통 파일만 복사하며 코드/DB를 수정하지 않습니다.
4. `python -m pip install -r requirements.txt` 후 `python -m pip check`. 기존 CUDA PyTorch가 정상인지 재확인하세요. CUDA가 False면 CPU로 진행하지 않습니다. 필요한 모델 2개는 인터넷/캐시·VRAM 준비가 필요합니다.
5. `.env.example`을 `.env`로 복사한 후 실제 DATABASE_URL, OPENAI_API_KEY, LLM_MODEL을 입력합니다. API 키·비밀번호는 출력하거나 공유하지 않습니다. `LLM_MODEL`은 기존 수업에서 **실제 Tool Calling을 지원하는 모델 ID**로 설정합니다. 필요 시 기존 OpenAI 호환 endpoint의 OPENAI_BASE_URL을 별도로 설정합니다(제공 API가 LangChain ChatOpenAI와 호환되는지 확인).
6. pgAdmin에서 `report_agent_lab` DB를 선택해 `common/sql/01_read_only_check.sql` 실행. 기존 6종 카테고리, 3개 필수 개체, 유효한 ready 벡터 수 확인. 180건으로 맞추기 위해 재시드하지 마세요. `eligible_vectors=0`이면 강사에게 기존 DB 복구 방법을 문의하세요. Day30 자체는 수정하지 않습니다.

```bash
# 기존 정상 .venv를 사용하세요. 새 venv를 강제로 생성하거나 torch를 재설치하지 않습니다.
# 예시: 기존 가상환경의 실제 경로로 수정
source /c/workspace/your_project/.venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip check
cp .env.example .env
# VS Code에서 .env 값을 직접 수정
python -c "import torch; print(torch.cuda.is_available())"
```

## 3. 개발 및 실행 순서
`docs/IMPLEMENTATION_ORDER.md`의 단계별 계약 및 B/I/A 요구사항을 참조합니다.

```bash
python -m pytest -q                       # Fixture/단위 테스트
python -m scripts.preflight               # 설정, DB, CUDA (LLM 호출 없음)
python -m app.main                        # http://127.0.0.1:8000/docs
# 다른 터미널 / 프로젝트 루트
python -m scripts.verify_live             # 무료 DB/GPU 및 직접 DB Tool 테스트
python -m scripts.verify_live --allow-paid-llm  # 실제 RAG/Agent 유료 테스트(동의 시)
```
응용/심화 강사용 기준 평가: `python -m app.evaluation.retrieval_eval --k 3 --allow-paid-llm --generation` (유료). `--generation` 생략 시 검색 평가만 하되 Rewrite는 LLM 사용. 모든 실행 결과를 검토합니다.

## 4. 공통 자료 복사
`requirements.txt`, `.env.example`, `.gitignore`는 모든 단계 공통입니다. 평가용 `data/evaluation`은 응용/심화만 복사합니다. Common의 SQL은 pgAdmin에서 읽기 전용 점검용으로만 사용합니다. 상위 단계는 직접 만든 Python 소스와 함께 요구사항·테스트 계약을 충족합니다. `common/tests`의 reference tests는 제안 파일/함수명에 맞춘 선택적 검증 코드입니다. 구조를 다르게 설계했다면 import 및 test adapter만 수정하고 요구사항 판단 기준은 유지하세요.

## 5. Postman / 제출
`postman/`의 Collection, Environment를 Import합니다. `allow_paid_llm=false`에서는 유료 요청을 실행하지 않습니다. 현재 DB에서 존재하는 `report_id`와 존재하지 않는 `missing_report_id`를 직접 확인합니다. /health는 LLM configured와 live 성공이 다릅니다.
`docs/acceptance_checklist.csv`에 T-01~T-19 중 본인 난이도 결과를 기록합니다. `outputs/`의 실행 증거는 민감정보 제거 후 제출. 응답 200이나 단순 import 성공만으로 프로젝트 합격 처리하지 않습니다.

## 6. 운영 경계
- 로컬 127.0.0.1 전용. 인증/사용자별 접근 제어는 구현 대상이 아닙니다.
- 기존 DB는 조회만. Category는 검색 필터이지 보안 권한이 아닙니다.
- 예제 응답/고정 Fixture와 실제 CUDA·DB·LLM 호출을 구분합니다.
- 금요일 실습은 Multi-Agent/MCP/LangGraph StateGraph/영속 Memory/CRUD를 새로 구현하는 날이 아닙니다.
