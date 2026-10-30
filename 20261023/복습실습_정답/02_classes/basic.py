"""02 클래스 기본필수: 주문 하나 = 객체 하나. 속성 저장과 메서드 두 곳을 완성합니다."""

class Order:
    def __init__(self, item, unit_price, quantity):
        """정상 입력만 받습니다. __init__는 객체를 만들 때 자동 호출됩니다."""
        # 해설 C_B1: 받은 상품명·단가·수량을 이 객체의 속성에 저장하세요.
        # self는 지금 만들어지는 주문 객체입니다.
        # 매개변수는 함수가 끝나면 사라지므로 다음 호출에서도 쓸 값을 self에 보관합니다.
        self.item = item
        self.unit_price = unit_price
        self.quantity = quantity

    def amount(self):
        """인자는 따로 받지 않고 객체 안의 값을 계산에 사용합니다."""
        # 해설 C_B2: 이 주문 객체에 저장된 단가와 수량으로 금액을 반환하세요.
        # 다른 주문이 아니라 이 메서드를 호출한 객체의 값을 사용합니다.
        return self.unit_price * self.quantity


def main():
    first = Order("아메리카노", 3000, 2)
    second = Order("카페라떼", 4000, 1)
    print("첫 주문 금액:", first.amount())
    print("둘째 주문 금액:", second.amount())
    first.quantity = 3
    print("첫 주문 수량 변경 후:", first.amount())
    print("둘째 주문은 그대로:", second.amount())

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
