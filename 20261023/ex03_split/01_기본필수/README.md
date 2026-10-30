# 실습 03 · 60·20·20 분할과 무결성 검사 · 기본필수

PPT 27~35 (선택 85~86)쪽 · 해당 교시 실습 25분 · 현재 폴더: `ex03_split/01_기본필수`

**아직 구현하지 않은 학생 코드의 실패는 정상입니다.** TODO 번호를 찾아 완성하세요.

## 목표
100행을 60·20·20으로 나누고 ID 독립과 정답 정렬을 검사한다.

## 입력과 사전 준비
`data/requests.csv` (원본 순서 유지)



## 구현 위치와 함수 계약
**`main.py::split_xy` — D5-03-B1**

같은 호출로 X,y를 두 번 나눕니다. 반환: {train:(X_train,y_train), valid:(X_valid,y_valid), test:(X_test,y_test)}. 1차 test_size=0.20, 2차 개발용의 test_size=0.25, 각 단계 stratify를 적용합니다.

**`main.py::check_parts` — D5-03-B2**

각 부분의 ID 고유성·교집합 없음·전체 포함·X/y index 순서 일치를 검사합니다. 잘못되면 ValueError, 올바르면 True. 단순 행 수만 맞춰서는 안 됩니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
두 번째 stratify는 y_dev입니다. 중복을 set으로 바꾸기 전에 각 index.is_unique도 확인하세요.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 03 --level basic
python tools/check.py --exercise 03 --level basic
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.

