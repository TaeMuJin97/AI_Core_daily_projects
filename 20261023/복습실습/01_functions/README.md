# 01 함수 활용


**꼭 구분할 것:** 함수를 정의하는 것과 호출하는 것은 다릅니다. `return`은 호출한 곳에 값을 주고,
`print`는 화면에 보여 줍니다. `price`, `quantity`는 함수가 받은 입력입니다.

```python
amount = calculate_amount(3000, 2)
print(amount)
```

위 코드에서 `amount`에 들어갈 값을 먼저 적습니다. 함수 내부의 매개변수 이름을 바꾸는 것이 아니라
호출할 때 넘기는 3000과 2를 바꿔서 재실험합니다.

**기본필수 추가 반복:** 수량 2→3, 단가 3000→2000으로 각각 바꾸고 예측값·실행값을 비교합니다.
같은 함수 세 개로 계속 반복해도 됩니다.

### 기본필수

열 파일: [`01_functions/basic.py`](basic.py)  
직접 채울 곳: **F_B1, F_B2, F_B3**

```text
python 01_functions/basic.py
python check.py 01_basic
```

**완료 시 확인할 값:** 금액 6000 / 문장 “쿠키: 6000원” / 함수 연결 “카페라떼: 8000원”

**설명 질문:** 어떤 줄이 함수를 호출하나요? return 대신 print만 쓰면 amount에는 무엇이 들어갈까요?

화면 출력 대조: [`expected/01_functions/basic.txt`](../expected/01_functions/basic.txt)

<details><summary>F_B1 · 힌트 1</summary><p>3000원짜리 음료 2개의 금액을 먼저 손으로 계산합니다.</p></details>

<details><summary>F_B1 · 힌트 2</summary><p>반환할 값은 price와 quantity의 곱입니다. 함수 안에서 출력하지 않습니다.</p></details>

<details><summary>F_B2 · 힌트 1</summary><p>반환 자료형은 int가 아니라 str입니다.</p></details>

<details><summary>F_B2 · 힌트 2</summary><p>f 문자열을 사용해 상품명, 콜론, 공백, 금액, 원을 차례로 연결합니다.</p></details>

<details><summary>F_B3 · 힌트 1</summary><p>두 함수의 입력과 반환값을 화살표로 이어 봅니다.</p></details>

<details><summary>F_B3 · 힌트 2</summary><p>금액 계산 → 그 금액으로 문장 만들기 → 그 문장 반환. 이미 만든 함수를 다시 사용합니다.</p></details>

### 선택 응용

열 파일: [`01_functions/applied.py`](applied.py)  
직접 채울 곳: **F_A1, F_A2**

```text
python 01_functions/applied.py
python check.py 01_applied
```

**완료 시 확인할 값:** 주문 3건의 총액 16000 / 6000원 이상 주문 2건 / 빈 목록 합계 0

**설명 질문:** return이 for문 안에 있으면 두 번째·세 번째 주문은 계산되나요?

화면 출력 대조: [`expected/01_functions/applied.txt`](../expected/01_functions/applied.txt)

<details><summary>F_A1 · 힌트 1</summary><p>total=0에서 시작한 뒤 각 주문의 금액을 누적합니다.</p></details>

<details><summary>F_A1 · 힌트 2</summary><p>for 안에서는 더하기, for가 끝난 뒤에는 return을 둡니다. 빈 목록은 0입니다.</p></details>

<details><summary>F_A2 · 힌트 1</summary><p>기준 금액과 정확히 같아도 포함합니다.</p></details>

<details><summary>F_A2 · 힌트 2</summary><p>주문 하나의 금액을 계산하고 &gt;= minimum일 때 count를 1 올립니다.</p></details>

### 선택 심화

열 파일: [`01_functions/advanced.py`](advanced.py)  
직접 채울 곳: **F_D1, F_D2**

```text
python 01_functions/advanced.py
python check.py 01_advanced
```

**완료 시 확인할 값:** 유효 수량 합 5 / 제외 7건 / 원본 값 9개 유지

**설명 질문:** None과 0은 이 실습에서 어떻게 다른가요? 잘못된 값을 조용히 0으로 만들지 않는 이유는 무엇인가요?

화면 출력 대조: [`expected/01_functions/advanced.txt`](../expected/01_functions/advanced.txt)

<details><summary>F_D1 · 힌트 1</summary><p>int로 바꿀 수 있는지와 1 이상인지를 각각 확인합니다.</p></details>

<details><summary>F_D1 · 힌트 2</summary><p>문자열·정수만 허용합니다. None, bool, float는 제외하고 변환 실패는 None으로 표시합니다.</p></details>

<details><summary>F_D2 · 힌트 1</summary><p>None은 0이라는 뜻이 아니라 사용할 수 없다는 표시입니다.</p></details>

<details><summary>F_D2 · 힌트 2</summary><p>각 값에 parse_quantity를 호출하고 None이면 제외 건수를, 아니면 합계를 올립니다.</p></details>

명령은 이 단원 폴더가 아니라 전체 역할 폴더(README가 있는 위치)의 터미널 기준입니다.
