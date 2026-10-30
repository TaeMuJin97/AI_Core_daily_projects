# 실습 06 · 열별 전처리와 기준선 연결 · 기본필수

PPT 55~65쪽 · 해당 교시 실습 25분 · 현재 폴더: `ex06_pipeline/01_기본필수`

**완성된 정답 코드입니다.** 해설 주석을 읽고 학생에게 정답을 바로 제시하기보다 아래 완료 조건을 먼저 확인하게 하세요.

## 목표
수치 2열과 범주 6열을 연결해 변환된 8열과 행 ID를 확인한다.

## 입력과 사전 준비
`data/checkpoints/train.csv`·`valid.csv` 및 코드 안의 작은 배열
04~06의 고정 체크포인트는 전처리 전 자료입니다. 이전 실습 소스의 완성 여부와 무관하게 진행합니다.


## 구현 위치와 함수 계약
**`main.py::make_preprocessor` — D5-06-B1**

NUM은 prior_numeric(), CAT은 prior_categorical()에 연결합니다. 경로 이름 num/cat, remainder='drop'인 미학습 ColumnTransformer를 반환합니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
열별 분기는 ColumnTransformer, 각 경로의 순서는 Pipeline입니다. 나머지 열이 자동 입력되지 않도록 remainder를 확인하세요.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 06 --level basic
python tools/check.py --exercise 06 --level basic
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.
## 강사용 설명
입력 X 4열이 수치 2 + 작업유형 3 + 우선순위 3 = 8열이 된다. get_feature_names_out()으로 순서를 확인하고 DataFrame에 기존 request_id index를 다시 붙인다.
