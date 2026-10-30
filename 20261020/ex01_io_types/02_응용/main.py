# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 01 | 응용
# 소계·학습용 부가세·최종 금액 | PPT 21쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

unit_price = int(input("단가(원): "))
quantity = int(input("수량: "))
delivery = int(input("배송비(원): "))
# TODO 01: 단가와 수량으로 소계를 계산하세요.
subtotal = unit_price * quantity
# TODO 02: 배송비를 제외한 소계의 10%를 계산하세요.
vat = subtotal * 0.1
# TODO 03: 소계·부가세·배송비를 합산하세요.
total = subtotal + vat + delivery
# TODO 04: 금액을 천 단위 쉼표·소수점 한 자리로 출력하세요.
# print("TODO: 세 가지 금액을 출력하세요.")
print(f"소계: {subtotal:,}")
print(f"부가세: {vat:,}")
print(f"최종 금액: {total:,}")