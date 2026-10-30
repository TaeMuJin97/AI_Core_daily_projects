# 03 CSV·JSON 읽기·정제·집계·저장


**하나의 처리 흐름:** 읽기 → 공백/자료형 정리 → 금액 계산 → 합계 → 저장 → 다시 읽기.
먼저 `data/orders_basic.csv`와 `data/orders_basic.json`을 VS Code에서 텍스트로 엽니다.
CSV 3건과 JSON 2건은 서로 다른 거래이므로 연결하면 5건입니다.

| ID | 상품 | 단가 | 수량 | 예상 금액 |
|---|---|---:|---:|---:|
| C01 | 아메리카노 | 3000 | 2 | 6000 |
| C02 | 카페라떼 | 4000 | 1 | 4000 |
| C03 | 쿠키 | 2000 | 3 | 6000 |
| J01 | 아메리카노 | 3000 | 1 | 3000 |
| J02 | 카페라떼 | 4000 | 2 | 8000 |

CSV의 숫자 문자열을 그대로 더하면 원하는 계산이 되지 않습니다.
`int("2")`는 정수 2, `" 쿠키 ".strip()`은 공백이 없는 “쿠키”입니다.
`read_csv`, `read_json`, `save_results`의 파일 열고 닫는 부분은 제공했습니다.
읽기 함수들을 호출하고 정제·집계를 구현하는 데 집중합니다.

**원본 보존:** `data`는 수정하지 않습니다. 새 행을 만들어 `outputs`에 저장합니다.
수량 누락·중복 처리는 응용·심화에서만 다룹니다. 기본필수에서 한꺼번에 해결하지 않습니다.
**기본필수 추가 반복:** 입력 파일 사본에서 한 수량만 바꾸고 결과가 얼마나 달라질지 먼저 적어 봅니다.

### 기본필수

열 파일: [`03_files/basic.py`](basic.py)  
직접 채울 곳: **D_B1, D_B2, D_B3**

```text
python 03_files/basic.py
python check.py 03_basic
```

**완료 시 확인할 값:** 주문 5건 / 상품 9개 / 27000원 / CSV·JSON 재읽기 성공

**설명 질문:** 주문 5건과 수량 9개의 차이를 설명하고, 저장한 두 파일을 직접 열어 보세요.

화면 출력 대조: [`expected/03_files/basic.txt`](../expected/03_files/basic.txt)

<details><summary>D_B1 · 힌트 1</summary><p>read_csv와 read_json은 위에서 import한 제공 함수입니다.</p></details>

<details><summary>D_B1 · 힌트 2</summary><p>각각 반환하는 List 두 개를 +로 연결합니다. CSV 뒤에 JSON을 붙입니다.</p></details>

<details><summary>D_B2 · 힌트 1</summary><p>strip은 양끝 공백을 제거합니다. int는 숫자 문자열을 정수로 바꿉니다.</p></details>

<details><summary>D_B2 · 힌트 2</summary><p>새 Dict에는 order_id·item·unit_price·quantity·amount 다섯 키를 넣습니다.</p></details>

<details><summary>D_B3 · 힌트 1</summary><p>주문 5건과 상품 9개는 다른 수치입니다.</p></details>

<details><summary>D_B3 · 힌트 2</summary><p>len(rows)는 주문 수입니다. 수량과 금액은 각각 별도 변수에 더합니다.</p></details>

### 선택 응용

열 파일: [`03_files/applied.py`](applied.py)  
직접 채울 곳: **D_A1, D_A2**

```text
python 03_files/applied.py
python check.py 03_applied
```

**완료 시 확인할 값:** 10행 → 정상 5·제외 5 / 아메리카노 9000·카페라떼 12000·쿠키 6000원

**설명 질문:** 수량이 없는 주문을 0개로 처리하지 않고 제외 이유에 남기는 이유는 무엇인가요?

화면 출력 대조: [`expected/03_files/applied.txt`](../expected/03_files/applied.txt)

<details><summary>D_A1 · 힌트 1</summary><p>check_row는 (정제 행, 이유)를 반환합니다. 성공하면 이유는 None입니다.</p></details>

<details><summary>D_A1 · 힌트 2</summary><p>실패는 rejected에 원본·이유를 담고, 성공은 clean에 checked를 담습니다.</p></details>

<details><summary>D_A2 · 힌트 1</summary><p>처음 본 상품이면 누적할 두 값을 0으로 준비합니다.</p></details>

<details><summary>D_A2 · 힌트 2</summary><p>상품명을 바깥 Dict의 키로 쓰고 안쪽 quantity와 amount에 더합니다.</p></details>

### 선택 심화

열 파일: [`03_files/advanced.py`](advanced.py)  
직접 채울 곳: **D_D1, D_D2**

```text
python 03_files/advanced.py
python check.py 03_advanced
```

**완료 시 확인할 값:** 14행 → 정상 6·보류 포함 제외 8 / 31000원 / 이유별 4·1·1·2건

**설명 질문:** 내용이 다른 같은 ID의 거래는 자동으로 어느 쪽을 믿을 수 있나요? 원본과 이유를 어떻게 남겼나요?

화면 출력 대조: [`expected/03_files/advanced.txt`](../expected/03_files/advanced.txt)

<details><summary>D_D1 · 힌트 1</summary><p>잘못된 첫 행 때문에 뒤의 정상 행까지 제외하지 않도록 유효성 검사를 먼저 합니다.</p></details>

<details><summary>D_D1 · 힌트 2</summary><p>정상 행의 ID가 seen_ids에 있으면 보류. 없다면 seen_ids와 clean에 함께 추가합니다.</p></details>

<details><summary>D_D2 · 힌트 1</summary><p>개별 데이터가 아니라 rejected 안의 reason을 셉니다.</p></details>

<details><summary>D_D2 · 힌트 2</summary><p>같은 이유를 만나면 기존 값에 1을 더합니다. 빈 목록이면 빈 Dict입니다.</p></details>

명령은 이 단원 폴더가 아니라 전체 역할 폴더(README가 있는 위치)의 터미널 기준입니다.
