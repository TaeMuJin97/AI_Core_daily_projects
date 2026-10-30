# 실습 03 · 60·20·20 분할과 무결성 검사 · 응용

PPT 27~35 (선택 85~86)쪽 · 해당 교시 실습 25분 · 현재 폴더: `ex03_split/02_응용`

**아직 구현하지 않은 학생 코드의 실패는 정상입니다.** TODO 번호를 찾아 완성하세요.

## 목표
분할 건수·클래스·seed·ID 순서를 기록하고 원본 행 순서의 영향을 확인한다.

## 입력과 사전 준비
`data/requests.csv` (원본 순서 유지)



## 구현 위치와 함수 계약
**`main.py::summarize_splits` — D5-03-A1**

seed, sizes, class_counts와 각 부분의 ID 순서(ids)를 JSON 저장 가능한 dict로 반환.

**`main.py::changed_training_ids` — D5-03-A2**

두 분할에서 train 소속이 달라진 ID 개수를 반환합니다(대칭차집합). 행 순서만 바꾼 별도 시연이며 기본 원본/분할표를 덮어쓰지 않습니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
seed만 기록하지 말고 실제 소속 ID와 입력 파일/행 순서도 기록하세요. X와 y는 같이 뒤집습니다.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 03 --level applied
python tools/check.py --exercise 03 --level applied
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.

