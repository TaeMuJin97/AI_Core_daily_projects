# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 03 | 응용
# 결정표로 할인과 배송비 계산 | PPT 37쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

amount = int(input("구매금액(원): "))
member = input("회원(y/n): ")
coupon = input("쿠폰(y/n): ")

# [제공 코드] 이 단계에서는 회원/쿠폰 입력을 소문자 y 또는 n으로 제한한다.
if amount <= 0 or member not in ("y", "n") or coupon not in ("y", "n"):
    print("구매금액은 양수, 회원/쿠폰은 y 또는 n으로 입력하세요.")
else:
    # TODO 01: 할인 전 구매금액 50,000원 이상은 무료배송, 미만은 3,000원으로 정하세요.
    shipping = 0
    # TODO 02: 회원 10% 할인과 쿠폰 5,000원 할인을 각각 계산하세요.
    member_discount = 0.0
    coupon_discount = 0
    # TODO 03: 상품금액을 넘지 않도록 할인을 제한하고 결제금액을 계산하세요.
    discount = 0.0
    total = 0.0
    print(f"배송비: {shipping:,.1f}원")
    print(f"할인액: {discount:,.1f}원")
    print(f"결제금액: {total:,.1f}원")
