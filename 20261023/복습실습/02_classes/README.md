# 02 클래스 활용


**함수에서 한 걸음만 이동:** 아까는 가격과 수량을 매번 전달했습니다. 이제 주문 객체 안에 보관합니다.
`self`는 “이 주문”을 가리킵니다. 오늘은 상속이나 복잡한 설계 문법을 추가하지 않습니다.

```python
first = Order("아메리카노", 3000, 2)
second = Order("카페라떼", 4000, 1)
first.quantity = 3
```

수정 후 first.quantity와 second.quantity를 각각 적습니다.
`first.amount`는 메서드 자체이고, `first.amount()`는 호출 결과입니다. 괄호를 확인합니다.

**기본필수 추가 반복:** 첫 주문의 상품명과 수량을 바꿔도 둘째 주문이 그대로인지 확인합니다.

### 기본필수

열 파일: [`02_classes/basic.py`](basic.py)  
직접 채울 곳: **C_B1, C_B2**

```text
python 02_classes/basic.py
python check.py 02_basic
```

**완료 시 확인할 값:** 첫 금액 6000 / 둘째 금액 4000 / 첫 수량 변경 후 9000 / 둘째는 4000 유지

**설명 질문:** 매개변수 quantity와 self.quantity의 역할이 어떻게 다르나요?

화면 출력 대조: [`expected/02_classes/basic.txt`](../expected/02_classes/basic.txt)

<details><summary>C_B1 · 힌트 1</summary><p>item과 self.item은 이름이 비슷하지만 쓰는 위치가 다릅니다.</p></details>

<details><summary>C_B1 · 힌트 2</summary><p>self.속성 = 매개변수 형태로 세 값을 각각 저장합니다.</p></details>

<details><summary>C_B2 · 힌트 1</summary><p>함수에서는 price를 받았지만 이번에는 self에 값이 저장되어 있습니다.</p></details>

<details><summary>C_B2 · 힌트 2</summary><p>self.unit_price와 self.quantity를 곱하고 return합니다.</p></details>

### 선택 응용

열 파일: [`02_classes/applied.py`](applied.py)  
직접 채울 곳: **C_A1, C_A2**

```text
python 02_classes/applied.py
python check.py 02_applied
```

**완료 시 확인할 값:** 쿠키 수량 4, 금액 8000 / 수량 0 변경은 거절 / 기존 수량 4 유지

**설명 질문:** 입력 검사를 한 뒤 대입해야 하는 이유는 무엇인가요?

화면 출력 대조: [`expected/02_classes/applied.txt`](../expected/02_classes/applied.txt)

<details><summary>C_A1 · 힌트 1</summary><p>검사보다 대입이 먼저 오면 잘못된 수량도 저장될 수 있습니다.</p></details>

<details><summary>C_A1 · 힌트 2</summary><p>정수인지, bool이 아닌지, 1 이상인지 확인하고 마지막에 self.quantity를 바꿉니다.</p></details>

<details><summary>C_A2 · 힌트 1</summary><p>키 네 개는 item, unit_price, quantity, amount입니다.</p></details>

<details><summary>C_A2 · 힌트 2</summary><p>금액은 이미 만든 self.amount()를 호출합니다. 기존 객체를 반환하는 것이 아닙니다.</p></details>

### 선택 심화

열 파일: [`02_classes/advanced.py`](advanced.py)  
직접 채울 곳: **C_D1, C_D2, C_D3**

```text
python 02_classes/advanced.py
python check.py 02_advanced
```

**완료 시 확인할 값:** 첫 장바구니 12000 / 둘째 0 / 두 목록은 서로 다른 객체

**설명 질문:** 목록을 __init__ 밖에 함께 만들면 무엇이 공유될 수 있나요?

화면 출력 대조: [`expected/02_classes/advanced.txt`](../expected/02_classes/advanced.txt)

<details><summary>C_D1 · 힌트 1</summary><p>첫 번째 장바구니에 넣은 주문이 두 번째에 나타나면 안 됩니다.</p></details>

<details><summary>C_D1 · 힌트 2</summary><p>self.orders = 빈 목록을 __init__ 안에 둡니다.</p></details>

<details><summary>C_D2 · 힌트 1</summary><p>List에 원소 하나를 추가하는 메서드는 append입니다.</p></details>

<details><summary>C_D2 · 힌트 2</summary><p>추가 대상은 self.orders, 추가할 값은 order입니다.</p></details>

<details><summary>C_D3 · 힌트 1</summary><p>Dict의 order[&quot;amount&quot;]가 아니라 객체의 메서드를 호출합니다.</p></details>

<details><summary>C_D3 · 힌트 2</summary><p>빈 장바구니는 total의 시작값인 0을 그대로 반환합니다.</p></details>

명령은 이 단원 폴더가 아니라 전체 역할 폴더(README가 있는 위치)의 터미널 기준입니다.
