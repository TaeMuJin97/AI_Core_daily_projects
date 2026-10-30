"""02 클래스 심화(선택): 상속 대신 객체를 List에 담아 협력시킵니다."""

class Order:
    def __init__(self, item, unit_price, quantity):
        self.item = item
        self.unit_price = unit_price
        self.quantity = quantity

    def amount(self):
        return self.unit_price * self.quantity


class Cart:
    def __init__(self):
        # 해설 C_D1: 장바구니 객체마다 독립적인 빈 목록을 만드세요.
        # 클래스 바깥이나 클래스 속성으로 []를 만들면 여러 객체가 공유하기 쉽습니다.
        # __init__ 안에서 만들면 Cart()마다 새 List가 생깁니다.
        self.orders = []

    def add(self, order):
        """입력은 이미 만든 Order 객체입니다. 문자열이나 Dict가 아닙니다."""
        # 해설 C_D2: 전달받은 주문 객체를 이 장바구니에 추가하세요.
        # 주문의 복사본을 만드는 것이 아니라 받은 객체를 담습니다.
        self.orders.append(order)

    def total_amount(self):
        # 해설 C_D3: 장바구니 안의 주문 금액을 모두 더해 반환하세요.
        total = 0
        for order in self.orders:
            # List 속 각 원소는 Dict가 아니라 Order 객체입니다.
            total = total + order.amount()
        return total


def main():
    first = Cart()
    second = Cart()
    first.add(Order("아메리카노", 3000, 2))
    first.add(Order("쿠키", 2000, 3))
    print("첫 장바구니 금액:", first.total_amount())
    print("둘째 장바구니 금액:", second.total_amount())
    print("서로 다른 목록:", first.orders is not second.orders)

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
