# 04 모듈형 일일 프로젝트

**오후 7~8교시 — 앞의 내용을 새로 공부하지 않고 이어 붙입니다.**

목표는 같은 주문 5건을 함수·객체·모듈로 나누어 처리하는 프로그램입니다.
앞 파일을 미완성으로 남겼어도 제공된 Order 클래스와 파일 읽기 코드로 시작할 수 있습니다.

```text
main.py         전체 순서 실행 + Dict를 Order 객체로 변환
   ↓
storage.py      CSV·JSON 읽기와 저장       (제공)
cleaning.py     공백·숫자 정제              (P_B1)
models.py       Order 클래스                (제공)
reporting.py    객체 목록을 집계            (P_B2)
main.py         위 기능 연결               (P_B3는 객체 생성)
```

`from models import Order`는 “models.py에서 Order를 가져와 사용한다”는 뜻입니다.
파일을 나눈 이유는 코드 길이를 늘리기 위해서가 아니라 읽기·정제·계산의 책임을 찾기 쉽게 하기 위해서입니다.

## 기본필수 — 세 곳만 완성

| 작성 순서 | 파일 | TODO | 입력 → 반환 |
|---|---|---|---|
| 1 | `04_project/cleaning.py` | P_B1 | 원본 Dict 목록 → 정제 Dict 목록 |
| 2 | `04_project/main.py` | P_B3 | 정제 Dict 목록 → Order 객체 목록 |
| 3 | `04_project/reporting.py` | P_B2 | Order 객체 목록 → 요약 Dict |

```text
python 04_project/main.py
python check.py 04_basic
```

**완료 결과:** 주문 5건 · 상품 9개 · 27000원.
`04_project/outputs/basic/clean_orders.csv`, `summary.json`, `rejected.json`을 확인합니다.
기본필수에서 제외한 행은 없으므로 rejected.json은 빈 목록입니다.
`expected/04_project/basic/`에 실제 정답 실행 결과가 있습니다.

## 선택 응용 — 상품별 요약 한 함수

`reporting.py`의 P_A1만 추가합니다. 기본필수와 같은 정상 5건을 사용합니다.
03 파일 응용의 불량 10행과 다릅니다. 새로운 입력 정제까지 동시에 추가하지 않습니다.

```text
python 04_project/main.py applied
python check.py 04_applied
```

아메리카노 3개·9000원 / 카페라떼 3개·12000원 / 쿠키 3개·6000원.

## 선택 심화 — 불량·중복 입력도 다루기

응용까지 완료한 뒤 `cleaning.py`의 P_D1을 추가합니다. 14행 중 정상 6건, 제외·보류 8건입니다.
첫 유효 ID를 유지하고 나중의 같은 ID는 원본과 함께 확인 대기로 남깁니다.

```text
python 04_project/main.py advanced
python check.py 04_advanced
```

상품 수량 11개, 집계 금액 31000원. 이 금액은 이번 실습의 임시 정제 정책을 적용한 값입니다.
실제 매출 확정 전에 중복·충돌 거래 확인이 필요함을 함께 기록합니다.

## 제출과 짝 확인

기본필수 프로그램과 결과 파일, `기록지/최종_설명.md`를 제출합니다.
짝은 작성자의 설명 없이 README의 실행 명령으로 실행한 다음 다음 질문을 합니다.

1. 금액 계산은 어느 함수/메서드가 담당하나요?
2. 왜 파일에서 읽은 숫자를 int로 바꾸었나요?
3. Order 객체와 Dictionary 중 어디에서 점(.)을 쓰나요?
4. 프로그램을 다시 실행해도 원본 data는 그대로인가요?

수행 속도나 선택 과제 개수로 순위를 매기지 않습니다. 수치 검사가 끝나면 본인 설명을 확인합니다.

프로젝트 폴더 안에서 실행할 때는 `python main.py`입니다. 전체 확인 도구는 상위 역할 폴더에 있습니다.
