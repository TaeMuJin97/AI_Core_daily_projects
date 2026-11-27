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

먼저 단계별 검증 파일을 프로젝트 루트로 복사합니다. 압축 최상위 폴더에서 (프로젝트 경로는 선택한 난이도에 맞게 변경):

```bash
python common/prepare_project.py mentee/01_basic
cd mentee/01_basic
```

새 빈 프로젝트를 직접 만드는 경우 실제 common 경로의 `test/`, `pytest.ini` 및 공통 설정을 복사합니다. `test/README.md`에 번호별 명령과 실행 조건이 있습니다. 검증은 단계별로 실행하고 전체를 한꺼번에 실행하지 않습니다. 유료 검증에는 명시적인 `--allow-paid-llm`이 필요합니다.
1. 압축을 풀고 선택한 단계의 프로젝트 폴더를 VS Code에서 엽니다. **프로젝트 루트**에서 명령을 실행하세요 (`app/` 내부가 아님).
2. 기존 정상 CUDA PyTorch 가상환경을 선택/활성화합니다. 공통 `test/`를 복사한 뒤 `python -m test.000_test`로 인터프리터와 CUDA를 확인하세요.
3. 응용/심화는 아래 공통 파일(특히 `pytest.ini`)을 선택한 프로젝트 루트에 복사합니다. Basic/강사용은 환경 템플릿과 requirements가 이미 있습니다. `common/prepare_project.py`는 선택한 프로젝트 폴더에 공통 설정과 `test/` 검증 파일을 복사하며 업무 코드/DB를 수정하지 않습니다. 기존 파일을 덮어쓰지 않습니다.
4. CUDA PyTorch를 **먼저** 확인합니다. 새 venv이거나 CPU 전용 torch이면 아래 GPU 준비 절차를 수행한 뒤 `python -m pip install -r requirements.txt`, `python -m pip check`를 실행하세요. 설치 전후 CUDA=True가 필수이며 CPU로 진행하지 않습니다. 모델 2개는 인터넷/캐시·VRAM 준비가 필요합니다.
5. `.env.example`을 `.env`로 복사한 후 실제 DATABASE_URL, OPENAI_API_KEY, LLM_MODEL을 입력합니다. API 키·비밀번호는 출력하거나 공유하지 않습니다. `LLM_MODEL`은 기존 수업에서 **Tool Calling과 provider-native Structured Output의 동시 사용을 지원하는 모델 ID**로 설정합니다. 필요 시 기존 OpenAI 호환 endpoint의 OPENAI_BASE_URL을 별도로 설정합니다(제공 API가 LangChain ChatOpenAI와 호환되는지 확인).
6. pgAdmin에서 `report_agent_lab` DB를 선택해 `common/sql/01_read_only_check.sql` 실행. 기존 6종 카테고리, 3개 필수 개체, 유효한 ready 벡터 수 확인. 180건으로 맞추기 위해 재시드하지 마세요. `eligible_vectors=0`이면 강사에게 기존 DB 복구 방법을 문의하세요. Day30 자체는 수정하지 않습니다.

```bash
# 기존 정상 .venv를 사용하세요. 새 venv를 강제로 생성하거나 torch를 재설치하지 않습니다.
# 예시: 기존 가상환경의 실제 경로로 수정
source /c/workspace/your_project/.venv/Scripts/activate
# CUDA 확인이 실패하면 아래 2-1 절을 먼저 수행
python -m test.000_test && python -m pip install -r requirements.txt && python -m pip check && python -m test.001_test
if [ ! -e .env ]; then cp .env.example .env; fi
# VS Code에서 .env 값을 직접 수정
```

### 2-1. CUDA PyTorch 준비 및 복구 (실제 강사 PC에서 CPU 빌드 문제 확인)

현재 터미널에서 `nvidia-smi`와 아래 명령으로 GPU, 인터프리터, PyTorch 빌드를 확인합니다.

```bash
nvidia-smi
python -m test.000_test
```

`+cpu`, `CUDA=None`, `False`가 표시되면 CPU 전용 PyTorch일 수 있습니다. `nvidia-smi`에서 GPU가 정상 표시되고 기존 CUDA 환경이 없다면, 프로젝트 전용 `.venv`에서 CUDA용 torch를 설치합니다. 새 venv에서 아직 torch가 없을 때는 제거 명령을 생략해도 됩니다. RTX 5080(Blackwell), CUDA 13.4 지원 드라이버 환경에서 권장하는 복구 예시는 아래 `cu130`입니다. 강사 PC의 실제 재설치 버전은 별도 기록하지 않았으므로 설치 후 직접 확인하세요. 다른 GPU/드라이버/Python이면 [PyTorch 공식 설치 선택기](https://pytorch.org/get-started/locally/)로 호환되는 빌드를 선택하세요. `nvidia-smi`의 CUDA 지원 표시와 PyTorch 빌드 버전은 같을 필요가 없습니다.

```bash
# 현재 프로젝트 전용 venv에서만 실행 (정상 CUDA 환경이면 이 블록 생략)
python -m pip uninstall -y torch torchvision torchaudio
python -m pip install torch --index-url https://download.pytorch.org/whl/cu130
python -m test.000_test && python -m pip install -r requirements.txt && python -m pip check && python -m test.001_test
```

이번 프로젝트는 torchvision/torchaudio를 직접 사용하지 않습니다. 기존 다른 프로젝트의 정상 venv에서는 무조건 삭제/재설치하지 마세요. CPU fallback이나 CUDA 검사 제거로 통과시키지 않습니다.

### 2-2. 실제 보고서 ID 저장

pgAdmin에서 유효한 ready 보고서와 실제 미존재 보고서 ID를 확인합니다. `.env`에 `DAY30_REPORT_ID=63`, `DAY30_MISSING_ID=999999`를 예시로 넣었으므로 자신의 DB 확인값으로 수정하세요. `load_settings()`는 새 터미널에서도 .env를 읽습니다. 이미 export한 값은 `.env`보다 우선합니다. Postman의 report_id/missing_report_id에도 같은 값을 지정하세요. Git Bash의 `$DAY30_REPORT_ID`는 .env를 Python이 읽는 것과 별개입니다. 명령에 `--report-id "$DAY30_REPORT_ID"`를 쓰려면 현재 터미널에서 먼저 export해야 합니다. 일반적으로 아래처럼 CLI 인자를 생략하거나 확인한 숫자를 직접 전달하면 됩니다.

## 3. 개발 및 실행 순서
`common/docs/IMPLEMENTATION_ORDER.md`의 현업형 Top-down 순서와 `test/README.md`의 번호별 검증을 참조합니다. 이미 완성된 Basic에는 002 초기 뼈대 전용 검증을 적용하지 않습니다.

```bash
python -m pytest tests/ -q -ra             # 선택한 프로젝트의 Fixture/단위 테스트만
python -m scripts.preflight               # 설정, DB, CUDA (LLM 호출 없음)
python -m app.main                        # http://127.0.0.1:8000/docs
# 다른 터미널 / 프로젝트 루트
python -m scripts.verify_live             # 무료 DB/GPU 및 직접 DB Tool 테스트
python -m scripts.verify_live --allow-paid-llm  # 실제 RAG/Agent 유료 테스트(동의 시)
```
응용/심화 강사용 기준 평가: `python -m app.evaluation.retrieval_eval --k 3 --allow-paid-llm --generation` (유료). `--generation` 생략 시 검색 평가만 하되 Rewrite는 LLM 사용. 모든 실행 결과를 검토합니다.

## 4. 공통 자료 복사
`requirements.txt`, `.env.example`, `.gitignore`, `pytest.ini`는 모든 단계 공통입니다. 선택한 프로젝트 루트에 `pytest.ini`를 두어 `testpaths = tests`가 적용되게 합니다. `common/tests` 전체와 프로젝트 `tests/`를 한 번에 수집하지 않습니다. `common/tests`를 참고할 경우 한 난이도만 골라 사용하세요. 평가용 `data/evaluation`은 응용/심화만 복사합니다. Common의 SQL은 pgAdmin에서 읽기 전용 점검용으로만 사용합니다. 상위 단계는 직접 만든 Python 소스와 함께 요구사항·테스트 계약을 충족합니다. `common/tests`의 reference tests는 제안 파일/함수명에 맞춘 선택적 검증 코드입니다. 구조를 다르게 설계했다면 import 및 test adapter만 수정하고 요구사항 판단 기준은 유지하세요.

## 5. Postman / 제출
`postman/`의 Collection, Environment를 Import합니다. `allow_paid_llm=false`에서는 유료 요청을 실행하지 않습니다. 현재 DB에서 존재하는 `report_id`와 존재하지 않는 `missing_report_id`를 직접 확인합니다. /health는 LLM configured와 live 성공이 다릅니다.
`docs/acceptance_checklist.csv`에 T-01~T-19 중 본인 난이도 결과를 기록합니다. `outputs/`의 실행 증거는 민감정보 제거 후 제출. 응답 200이나 단순 import 성공만으로 프로젝트 합격 처리하지 않습니다.

## 6. 운영 경계
- 로컬 127.0.0.1 전용. 인증/사용자별 접근 제어는 구현 대상이 아닙니다.
- 기존 DB는 조회만. Category는 검색 필터이지 보안 권한이 아닙니다.
- 예제 응답/고정 Fixture와 실제 CUDA·DB·LLM 호출을 구분합니다.
- 금요일 실습은 Multi-Agent/MCP/LangGraph StateGraph/영속 Memory/CRUD를 새로 구현하는 날이 아닙니다.
