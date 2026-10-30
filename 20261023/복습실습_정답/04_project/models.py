"""제공된 Order 클래스. 오전 실습을 떠올리며 읽고 main.py에서 사용하세요."""

class Order:
    def __init__(self, order_id, item, unit_price, quantity):
        self.order_id = order_id
        self.item = item
        self.unit_price = unit_price
        self.quantity = quantity

    def amount(self):
        return self.unit_price * self.quantity

    def to_dict(self):
        return {"order_id": self.order_id, "item": self.item,
                "unit_price": self.unit_price, "quantity": self.quantity,
                "amount": self.amount()}
