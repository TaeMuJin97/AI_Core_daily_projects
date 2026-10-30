# 실습 03 · 60·20·20 분할과 무결성 검사 · 심화

PPT 27~35 (선택 85~86)쪽 · 해당 교시 실습 25분 · 현재 폴더: `ex03_split/03_심화`

**아직 구현하지 않은 학생 코드의 실패는 정상입니다.** TODO 번호를 찾아 완성하세요.

## 목표
그룹 단위 분할과 과거→미래 검증의 차이를 코드로 확인한다.

## 입력과 사전 준비
`data/requests.csv` (원본 순서 유지)



## 구현 위치와 함수 계약
**`main.py::grouped_indices` — D5-03-H1**

E22: 그룹 1/3을 별도 holdout으로 배치하여 dev_idx, holdout_idx를 반환. test_size는 행 비율이 아니라 그룹 비율입니다. seed=42, n_splits=1.

**`main.py::time_indices` — D5-03-H2**

E23: 시간순 입력을 TimeSeriesSplit(n_splits=3)으로 나눈 index 쌍 목록 반환. 각 fold는 가장 늦은 훈련 index < 가장 이른 검증 index를 만족해야 합니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
두 예시는 본문 100행과 분리된 12행/8시점 예시입니다. 그룹의 개수와 행 수를 구분하세요.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 03 --level advanced
python tools/check.py --exercise 03 --level advanced
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.

