# Python 복습 실습 01

**오늘의 목표: 낯선 도구를 더 배우지 않고, 아는 코드를 작게 완성하여 끝까지 실행하기.**

수업 날짜는 고정하지 않은 재사용용 복습 자료입니다. 수업일은 강사가 기입합니다.
PPT 없이 **함수 → 클래스 → 파일 처리 → 모듈형 프로젝트**를 진행합니다.

## 가장 먼저

**브라우저로 `실습안내.html`을 여세요.** 코드 수정은 VS Code에서 합니다.
터미널의 현재 위치는 이 README가 있는 역할 폴더여야 합니다.

```text
python check_env.py
python 00_warmup.py
python 01_functions/basic.py
```

이번 예제는 추가 패키지를 사용하지 않습니다. 이미 있는 수업용 Python을 선택합니다.
`python`이 실행되지 않는 Windows 환경은 VS Code에서 기존 Python 실행기를 선택하고,
필요하면 같은 명령의 첫 부분을 `py`로 바꿉니다. macOS/Linux는 `python3`일 수 있습니다.
실제 검수 환경과 OS 범위는 강사용 검수 기록에 적습니다.

## 오늘 모두가 완성할 경로

| 순서 | 열 파일 | 완성 확인 | 확인 명령 |
|---|---|---|---|
| 오전 1 | `01_functions/basic.py` | 두 함수 연결로 카페라떼 8,000원 | `python check.py 01_basic` |
| 오전 2 | `02_classes/basic.py` | 한 객체만 바꾸어 다른 객체는 4,000원 유지 | `python check.py 02_basic` |
| 오후 1 | `03_files/basic.py` | 정제 5건 · 상품 9개 · 27,000원 저장 | `python check.py 03_basic` |
| 오후 2 | `04_project/cleaning.py`, `reporting.py`, `main.py` | 모듈을 연결해 같은 결과 재생성 | `python check.py 04_basic` |

**기본필수 11개 TODO만으로 하루 학습을 완료할 수 있습니다.**
응용·심화는 기본필수 설명까지 끝난 수강생의 선택입니다. 선택 과제 미수행은 미달이 아닙니다.

## 실행 원칙

한 번에 파일 하나, TODO 하나만 고칩니다. **출력 예상 → 수정 → 실행 → 한 문장 설명**을 반복합니다.
`NotImplementedError` 또는 `[아직 작성할 곳]`은 미완성 안내입니다.
확인 도구는 이를 '미완성'으로 구분하며 통과로 표시하지 않습니다.
`python check.py`로 확인 가능한 단원 목록을 봅니다. `all`은 주로 강사용 검사입니다.

## 폴더 안내

- `01_functions`, `02_classes`, `03_files`: 각각 basic / applied / advanced의 독립 실행 예제.
- `04_project`: 같은 프로젝트에 basic → applied → advanced 기능을 선택적으로 확장.
- `expected`: 실제 정답 실행의 화면 출력·결과 파일. 답안 소스가 아니라 대조 자료.
- `기록지`: 실행 전 예상, 막힌 지점, 최종 설명을 짧게 기록할 양식.
- `실습안내.html`: 단계별 질문, 작은 힌트, 실행 명령을 한 곳에서 보는 안내서.

프로젝트는 `python 04_project/main.py`로 기본필수를 실행합니다.
선택 응용은 끝에 `applied`, 선택 심화는 `advanced`를 붙입니다.
프로젝트 폴더만 따로 복사해도 실행할 수 있습니다. 루트의 확인 도구는 전체 역할 폴더에서 실행합니다.

## 최종 제출

수정한 기본필수 코드, `04_project/outputs/basic/clean_orders.csv`와 `summary.json`,
`기록지/최종_설명.md`를 제출합니다. Git 커밋이나 추가 보고서 분량은 필수가 아닙니다.
전체 합계만 맞추려고 27000을 하드코딩하지 마세요. 다른 정상 입력과 빈 목록도 처리해야 합니다.
