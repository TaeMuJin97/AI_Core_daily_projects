# 실습 01 · 문제 정의와 입력 열 선택 · 심화

PPT 12~16쪽 · 해당 교시 실습 20분 · 현재 폴더: `ex01_problem/03_심화`

**아직 구현하지 않은 학생 코드의 실패는 정상입니다.** TODO 번호를 찾아 완성하세요.

## 목표
요청/단계의 단위를 구분하고 라벨 관측 기간이 끝난 표본을 선별한다.

## 입력과 사전 준비
`data/requests.csv`와 `data/schema.csv`



## 구현 위치와 함수 계약
**`main.py::inspect_stages` — D5-01-H1**

한 요청의 단계 로그가 여러 행인지 진단합니다. 반환: rows, unique_requests, repeated_request_ids (정렬 목록).

**`main.py::mature_label_ids` — D5-01-H2**

UTC 관측 종료시각 <= as_of 이고 failed가 관측된(0/1) 요청 ID만 반환합니다. 관측 기간이 미완료이거나 정답 미확인인 행을 성공(0)으로 채우지 않습니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
groupby().size()로 요청별 행 수를 세고 관측 종료시각·정답 관측 여부를 함께 검사하세요. 관측 기간의 길이는 이 예제에 정해진 가정입니다.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 01 --level advanced
python tools/check.py --exercise 01 --level advanced
```

가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
`outputs/result.json` + 화면 출력 + `학습기록.md`

비교용: `expected_output.txt`와 `expected_outputs/result.json`
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.

