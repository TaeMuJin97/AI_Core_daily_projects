"""집계 담당 모듈. 주문 금액 계산은 Order.amount에 맡깁니다."""

def summarize_orders(orders):
    """입력은 Order 객체의 List입니다. 빈 목록은 모두 0으로 집계합니다."""
    # 해설 P_B2: 주문 객체 목록의 건수·수량·금액을 집계하세요.
    quantity = 0
    amount = 0
    for order in orders:
        quantity += order.quantity
        amount += order.amount()
    return {"order_count": len(orders), "total_quantity": quantity, "total_amount": amount}


def group_orders(orders):
    """선택 응용: {상품명: {quantity, amount}}를 반환합니다."""
    # 해설 P_A1: 주문 객체를 상품별로 집계하세요.
    groups = {}
    for order in orders:
        if order.item not in groups:
            groups[order.item] = {"quantity": 0, "amount": 0}
        groups[order.item]["quantity"] += order.quantity
        groups[order.item]["amount"] += order.amount()
    return groups
