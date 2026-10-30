"""02 클래스 응용: 수량 변경과 Dict 변환. 앞 실습과 독립적으로 실행됩니다."""

class Order:
    def __init__(self, item, unit_price, quantity):
        # 생성 시 입력은 정상이라고 가정합니다. 변경 메서드의 검증을 연습합니다.
        self.item = item
        self.unit_price = unit_price
        self.quantity = quantity

    def amount(self):
        return self.unit_price * self.quantity

    def set_quantity(self, quantity):
        """양의 정수만 허용합니다. 실패하면 ValueError, 원래 수량은 유지합니다."""
        # 해설 C_A1: 새 수량이 양의 정수인지 검사한 뒤 속성을 변경하세요.
        # 검사를 먼저 끝낸 뒤 대입해야 실패했을 때 기존 수량을 보존할 수 있습니다.
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("수량은 1 이상의 정수여야 합니다.")
        self.quantity = quantity

    def to_dict(self):
        """직렬화할 수 있는 기본 자료형으로 내용을 꺼냅니다."""
        # 해설 C_A2: 객체의 내용을 새 Dictionary로 반환하세요.
        # 객체 자체를 JSON으로 저장하기 전, 기본 자료형으로 옮기는 준비입니다.
        return {
            "item": self.item,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "amount": self.amount(),
        }


def main():
    order = Order("쿠키", 2000, 3)
    order.set_quantity(4)
    print("변경 후:", order.to_dict())
    try:
        order.set_quantity(0)
    except ValueError as error:
        print("입력 안내:", error)
    print("기존 수량 유지:", order.quantity)

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
