# 실습 06 · 열별 전처리와 기준선 연결 · 심화

PPT 55~65쪽 · 해당 교시 실습 25분 · 현재 폴더: `ex06_pipeline/03_심화`

**완성된 정답 코드입니다.** 해설 주석을 읽고 학생에게 정답을 바로 제시하기보다 아래 완료 조건을 먼저 확인하게 하세요.

## 목표
누락 열·추가 열·금지 열·미지 범주를 다른 상황으로 취급한다.

## 입력과 사전 준비
`data/checkpoints/train.csv`·`valid.csv` 및 코드 안의 작은 배열
04~06의 고정 체크포인트는 전처리 전 자료입니다. 이전 실습 소스의 완성 여부와 무관하게 진행합니다.


## 구현 위치와 함수 계약
**`main.py::validate_features` — D5-06-H1**

새 요청의 입력 계약을 검사하고 FEATURES 순서의 복사본을 반환합니다. 누락·중복 열, forbidden 열은 항상 ValueError. extra='error'면 나머지 추가 열도 오류. extra='drop'은 note 같은 일반 추가 열만 명시적으로 제외하며 forbidden은 여전히 오류입니다. 새로운 범주 값은 허용하되 필수 열 누락과 혼동하지 않습니다.

**`main.py::check_feature_names` — D5-06-H2**

출력 특성명이 고유하고 금지 입력에서 온 열이 없으면 True, 아니면 ValueError. num__ / cat__ 뒤 이름이 금지 이름 자체 또는 금지명+'_'로 시작하면 거부합니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
열 이름 정책과 열 값 정책은 다릅니다. drop 정책이 있어도 status 같은 미래 정보는 오류로 탐지하세요.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 06 --level advanced
python tools/check.py --exercise 06 --level advanced
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.
## 강사용 설명
priority가 없으면 입력 오류, note는 기본 오류/명시적 drop 가능, status는 항상 오류다. translation/urgent는 필수 열 안의 새 값이므로 기존 encoder로 처리한다. ColumnTransformer의 remainder=drop만 믿고 입력 감사를 생략하지 않는다.
