"""01 함수 응용: List 안의 Dict를 순회합니다. 기본필수 미완성이어도 독립 실행합니다."""

def calculate_amount(price, quantity):
    # 앞 시간 내용은 재제공합니다. 이번 목표는 반복문과 함수의 연결입니다.
    return price * quantity


def total_amount(orders):
    """입력: 주문 Dict의 List. 반환: 전체 금액(int). 빈 List는 0."""
    # TODO F_A1: 주문 목록을 순회하여 전체 금액을 반환하세요.
    raise NotImplementedError("F_A1: 주문 목록을 순회하여 전체 금액을 반환하세요.")


def count_large_orders(orders, minimum):
    """한 주문의 금액이 minimum 이상인 주문 개수를 반환합니다."""
    # TODO F_A2: 기준 금액 이상인 주문의 개수를 반환하세요.
    raise NotImplementedError("F_A2: 기준 금액 이상인 주문의 개수를 반환하세요.")


def main():
    orders = [
        {"item": "아메리카노", "unit_price": 3000, "quantity": 2},
        {"item": "카페라떼", "unit_price": 4000, "quantity": 1},
        {"item": "쿠키", "unit_price": 2000, "quantity": 3},
    ]
    print("전체 금액:", total_amount(orders))
    print("6000원 이상 주문:", count_large_orders(orders, 6000))
    print("빈 목록:", total_amount([]))

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
