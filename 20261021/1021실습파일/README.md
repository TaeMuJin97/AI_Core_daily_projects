# 2026.10.21 Day3 Python 실습 · 수강생용

소스의 TODO 블록을 직접 완성합니다. 아직 구현하지 않은 함수는 NotImplementedError로 표시되어 있습니다. 문법 오류가 아니라 미완성 표시입니다.

PPT 실습 01~08 × 기본필수/응용/심화 = **24개 독립 과제**입니다. 수업 중 모든 난이도를 다 하는 것이 아니라 기본필수를 우선하고 선택 확장합니다.
입력 예·예상 출력·공개 테스트를 제공하며, 수강생용에도 이전 단계 재사용 코드와 안전한 입출력 틀은 완성된 형태로 들어 있습니다.

## 1. 먼저 열 파일
이 역할 폴더를 VS Code의 **폴더 열기**로 엽니다. PPT_실습_대응표.md에서 본인의 실습을 찾고 해당 난이도의 README를 읽습니다.

## 2. 환경 준비 (Windows PowerShell)
Day2에서 만들었던 Python 3.13 가상환경을 그대로 재사용해도 됩니다. 새로 준비할 때:
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools/check_environment.py
```
`py`가 없으면 Python 버전을 먼저 확인하고 `python -m venv .venv`를 사용합니다.
VS Code 인터프리터는 해당 가상환경의 python.exe로 선택합니다. PowerShell 실행 정책을 바꾸지 않아도 실행기를 직접 지정할 수 있습니다.

macOS/Linux는 `python3 -m venv .venv` 뒤 `.venv/bin/python -m pip install -r requirements.txt`와 `.venv/bin/python tools/check_environment.py`를 사용합니다.
기준은 **Python 3.13.x · NumPy 2.3.5 · pandas 2.2.3**이며 requirements.txt가 직접 의존성을 고정합니다.
실습 01~04·07 및 프로젝트 기본필수는 외부 패키지 설치를 기다리는 동안에도 진행할 수 있습니다.
PPT의 다음 날 일정에 나온 NumPy/Pandas 최신 버전을 임의로 혼합하지 않습니다. 실제 검사 환경은 검수보고서에서 확인합니다.

## 3. 실행과 검사
아래 명령은 역할 폴더에서 실행하며 가상환경이 활성화되어 있을 때의 예입니다. 미활성화 시 python을 .\.venv\Scripts\python.exe로 바꿉니다.
```text
python tools/run.py --exercise 01 --level basic
python tools/check.py --exercise 01 --level basic
python tools/run.py --exercise 05 --level applied
python tools/check.py --exercise 05 --level applied
python tools/check.py --all --level basic
```
원본 실행 파일을 직접 실행해도 됩니다. 패키지형 실습 02·08은 day3_console에서 `python -m idea_app.main`이 정식 실행입니다.
제공 런처는 동일한 실행기를 선택해 경로 혼동을 줄여 줄 뿐 정답을 대신 구현하지 않습니다.

## 4. 단계 안의 파일
README.md: 요구사항·TODO 위치·함수 계약·실행 방법·완료 기준.
main.py 또는 day3_console/idea_app/: 구현할 소스. 해설/TODO 번호는 같은 기능을 가리킵니다.
checks.py: 공개 기능 검사. 기대값을 바꾸어 통과시키지 않습니다.
fixtures/: 정상·빈 데이터·손상/키 누락 등 테스트용 합성 자료. missing.json은 의도적으로 존재하지 않습니다.
expected_output.txt: 정답의 새 폴더 첫 실행 stdout. 프로젝트는 --demo 기준이며 sample_input은 별도 대화형 예입니다.
expected_outputs/: **정답을 실제로 실행해 만든** 파일 예시. 학습자가 자신의 생성 파일과 비교할 수 있습니다.
테스트_기록.md·리뷰_기록.md: 실제 수행한 내용과 각자 기여를 적는 양식.

## 5. 검사는 안전하게 분리합니다
```text
python tools/check.py --list
python tools/check.py --exercise 08 --level advanced
python tools/check.py --all --report reports/check_result.json
python tools/check.py --all --syntax-only
```
각 단계를 임시 폴더에 복사하여 별도 Python 프로세스에서 검사합니다. 학습자가 수정한 원본·결과물을 검사로 덮어쓰지 않습니다.
--all은 미실시 난이도까지 검사합니다. TODO/FAIL은 아직 구현하지 않은 블록 또는 실패한 테스트를 의미합니다.
--syntax-only는 문법만 검사하며 기능 완료 판정이 아닙니다. 체크리스트·리뷰 내용·실제 GitHub 활동은 사람이 확인합니다.
실습 07 기본필수의 PASS는 의도적 결함의 재현 성공이지 그 결함 코드를 실무에 써도 된다는 뜻이 아닙니다.

## 6. 일일 프로젝트
```text
python tools/run.py --exercise 08 --level basic
python tools/run.py --exercise 08 --level applied --demo --workspace ./trial_02
python tools/run.py --exercise 08 --level applied --show --workspace ./trial_02
```
workspace는 실행되는 day3_console을 기준으로 해석됩니다. --demo는 기존 data/ideas.json을 덮어쓰지 않습니다.
기본 메뉴의 5=저장, 0=종료입니다. 종료는 자동 저장이 아닙니다.
처음 파일이 없을 때는 빈 목록으로 시작하며, 손상 파일을 불러오지 못하면 저장을 차단합니다.
소스·합성 3건의 JSON·보고서·테스트·리뷰 기록·개인 기여를 제출합니다. 심화는 test_cases.py도 직접 완성합니다.

## 7. 오늘의 범위
실제 Multi AI Agent 호출이 아니라 Agent 아이디어/역할을 관리할 코드 구조와 데이터 처리 기초입니다.
GitHub 온라인/오프라인 활동은 GitHub_활동안내.md를 따릅니다. 실제 커밋/PR을 생성하지 않았으면 미실시로 표시합니다.
Matplotlib·CSV 심화·로컬 Git 명령은 10월 22일 수업으로 연결합니다.
API 키·GPU·유료 서비스는 필요하지 않습니다. .venv·비밀정보·개인정보를 압축해 제출하지 않습니다.
