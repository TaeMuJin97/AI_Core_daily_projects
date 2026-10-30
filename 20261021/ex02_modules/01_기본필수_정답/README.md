# 실습 02 · 클래스를 모듈로 분리하기 · 기본필수

**PPT 실습 22쪽 · 설명 14~23쪽 · 전체 단계 선택 실습 20분**

## 목표
Idea를 models.py, 실행을 main.py에 배치하고 패키지 루트에서 python -m idea_app.main으로 실행합니다.

## 진행 순서
먼저 동작을 예측하고, 아래 TODO를 구현합니다. 직접 실행 → 공개 검사 → 페어 설명/기록 순서로 마칩니다.
TODO가 아닌 입출력 틀·검사 도구·이전 단계 구현은 제공 코드입니다. 파일 간 책임을 바꾸지 않고 핵심 처리부터 완성합니다.

| 수정할 파일 | TODO/해설 번호 | 구현할 내용 |
|---|---|---|
| `day3_console/idea_app/models.py` | `INIT` | name·problem의 공백을 제거하고 roles를 새 List로 복사해 네 속성을 저장하세요. |
| `day3_console/idea_app/models.py` | `SUMMARY` | '이름: 역할 N개' 형태의 문자열을 반환하세요. print하지 않습니다. |
| `day3_console/idea_app/main.py` | `MAIN` | Idea 두 개를 만들고 catalog에 등록한 뒤 names() 결과를 출력하세요. |

## 실행
가상환경의 Python으로 실행합니다. 현재 난이도 폴더에서:

```text
cd day3_console
python -m idea_app.main
```

역할 폴더(강사용 또는 수강생용)에서 제공 런처를 사용할 때:

```text
python tools/run.py --exercise 02 --level basic
python tools/check.py --exercise 02 --level basic
```

`checks.py`는 기능 확인용 제공 테스트입니다. 검사 도구는 임시 복사본에서 실행하여 원본 소스와 결과물을 변경하지 않습니다.
출력 기대값은 `expected_output.txt`, 생성 파일 예시는 `expected_outputs/`를 확인합니다. 구현을 하드코딩해 예시 한 건만 맞추지 마세요.

## 생성할 결과
화면 출력과 학습/리뷰 기록. 생성할 파일이 없는 단계입니다.

### 패키지 실행 위치
`day3_console`에서 `python -m idea_app.main`으로 실행합니다.
`idea_app/main.py`를 하위 폴더에서 바로 실행하여 ModuleNotFoundError가 나면 먼저 실행 위치를 점검합니다.
루트의 tools/run.py 또는 제공된 day3_console/run_console.py는 위치 혼동을 줄이는 런처입니다.
models는 상태, service는 등록·조회, main은 화면 출력을 맡습니다. 심화의 Agent.run은 추상 계약이므로 그 메서드 자체의 NotImplementedError는 의도된 것입니다.

### 확인
다른 모듈에서 import했을 때 입력 대기·출력·파일 쓰기가 발생하지 않아야 합니다. 이름을 json.py/numpy.py/pandas.py로 짓지 않습니다.


## 완료 확인
구현한 범위의 자동 테스트가 통과하고, 테스트_기록.md에 실제 명령/결과를 기록했는지 확인합니다.
코드를 설명하지 못한 채 출력만 맞춘 경우에는 페어에게 입력 → 처리 → 반환/저장의 순서를 설명해 봅니다.

강사용: 각 `해설` 번호는 수강생 TODO와 대응합니다. `예상 출력`은 실제 정답 실행 결과이며 학생 기록의 대필용으로 배포하지 않습니다.
