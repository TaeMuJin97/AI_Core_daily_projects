# Day2 Python 실습 · 수강생용

이 폴더를 VS Code에서 **폴더 열기**로 엽니다. 각 실습 폴더 안에는 기본필수·응용·심화가 있습니다.
소스의 TODO 부분을 완성합니다. 임시 값이나 NotImplementedError가 남아 있으면 아직 구현 전입니다. 정답 소스는 이 폴더에 들어 있지 않습니다.

## 1. 실행 환경

수업 목표 실행기는 Python 3.13입니다. 이 자료의 정답 검증 환경은 별도 검수 보고서에 실제 값으로 기록합니다.
PowerShell에서 Python Launcher를 사용할 수 있을 때:

```powershell
py -3.13 --version
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe --version
```

`py` 명령이 없지만 Python이 이미 설치되어 있으면 `python --version`을 먼저 확인하고 `python -m venv .venv`를 사용합니다.
VS Code의 `Python: Select Interpreter`에서 `.venv\Scripts\python.exe`를 선택합니다.
**PPT 11쪽의 `.venvScriptspython.exe`는 경로 구분자가 빠진 표기입니다. 실제 경로는 `.venv\Scripts\python.exe`입니다.**

활성화를 지원하는 환경에서는 `.\.venv\Scripts\Activate.ps1`을 실행합니다.
보안 정책 때문에 활성화 스크립트가 막히면 정책을 무작정 바꾸지 말고 아래처럼 실행기를 직접 지정합니다.

```powershell
.\.venv\Scripts\python.exe "ex00_environment/01_기본필수/hello.py"
```

macOS/Linux에서는 `python3 -m venv .venv` 후 `.venv/bin/python`을 사용합니다.
가상환경 폴더는 압축파일에 넣지 않았습니다. 사용자의 PC에서 직접 만듭니다.

## 2. PPT의 패키지 준비

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements_environment.txt
.\.venv\Scripts\python.exe -m pip list
```

오늘 실습 01~07은 외부 패키지를 import하지 않으므로 설치 대기 중에도 진행할 수 있습니다.
`requirements_environment.txt`는 PPT 10쪽에 맞춘 **설치 준비 목록**이며 버전 잠금 파일은 아닙니다.
`requirements.txt`는 오늘 과제에 외부 의존성이 없음을 기록합니다. 다음 데이터 처리 강의의 호환 버전은 별도로 관리합니다.

## 3. 진행 예시

`.venv`를 활성화한 터미널 또는 해당 실행기를 선택한 환경에서:

```powershell
python "ex01_io_types/01_기본필수/main.py"
python tools/check.py --exercise 01 --level basic
```

활성화 없이 실행할 때는 위의 `python`을 `.\.venv\Scripts\python.exe`로 바꿉니다.
기본필수는 공통 출발점입니다. 응용·심화는 목표에 맞게 선택하며 각 단계는 **독립 실행** 가능합니다.
실습 00은 `hello.py`/`env_check.py`, 그 밖의 핵심 과제는 `main.py`입니다.

## 4. 폴더 안의 파일

`README.md`: 요구사항·단계별 작업·실행법·완료 기준.
`sample_input.txt`: 키보드 입력 예시. 한 줄씩 입력합니다. 입력이 없는 과제는 빈 파일입니다.
`expected_output.txt`: 정답 프로그램의 stdout 결과. 입력 echo가 없으므로 프롬프트가 이어 보일 수 있습니다.
`실행예.txt`: 입력 내용까지 보이는 대화형 실행 예.
`main.py` 또는 `hello.py`: 직접 실행하거나 완성할 코드.
문서의 TODO는 생각과 기록을 작성할 곳이며, source의 TODO는 실제 구현할 곳입니다.

## 5. 검사 방법

```powershell
python tools/check.py --list
python tools/check.py --exercise 05 --level applied
python tools/check.py --all
```

검사 도구는 표준 라이브러리만 사용합니다. 하위 프로세스에 입력을 공급하고 정상/경계 결과를 비교합니다.
메뉴가 끝나지 않으면 8초 뒤 시간 초과로 표시합니다. 정답 전체 검사는 몇 초~수십 초가 걸릴 수 있습니다.
검사는 각 파일을 독립 실행하며, 함수 과제는 반환값과 원본 변경 여부도 점검합니다.
수강생이 아직 시작하지 않은 다른 난이도까지 --all로 검사하면 FAIL이 많이 나오는 것이 정상입니다.

## 6. 제출

완성한 단계의 소스와 실습 07의 `제출_보고서.md`를 제출합니다. 심화는 `test_cases.py`·함수 표·구조도도 제출합니다.
출력 화면 또는 실제 테스트 기록을 남기고 두 사람의 역할·수정 기여를 각각 기록합니다.
`.venv`, `__pycache__`, 개인 토큰·키는 제출하지 않습니다. 이 실습은 계정·결제·API 키를 요구하지 않습니다.

## 7. 범위와 보충 규칙

이번 프로젝트는 **Multi AI Agent 아이디어 관리 도구**이지 실제 Agent 실행 시스템이 아닙니다.
파일 저장·클래스·실제 모듈 분리는 다음 수업 범위이므로 필수로 요구하지 않습니다.
초기 숫자 입력 과제는 정해진 자료형을 입력하는 계약을 사용합니다. 문자열 숫자 변환 오류를 모두 try/except로 감싸는 과제는 아닙니다.
검사 도구의 argparse·json·subprocess·import 등은 강사가 제공한 보조 코드이며 오늘의 평가 대상이 아닙니다.
