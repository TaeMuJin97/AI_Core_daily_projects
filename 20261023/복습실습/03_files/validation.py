"""제공 코드: 한 행의 검증. 응용·심화에서 호출하여 이유를 기록합니다."""


def positive_int(value):
    """양의 정수 또는 그 문자열만 허용. bool·float·누락·0·음수는 None."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        number = int(value)
    except ValueError:
        return None
    if number <= 0:
        return None
    return number


def check_row(row):
    """반환: (정제된 새 Dict, None) 또는 (None, 제외 이유). 원본은 바꾸지 않음."""
    if not isinstance(row, dict):
        return None, "행 형식 오류"
    order_id = row.get("order_id")
    item = row.get("item")
    if not isinstance(order_id, str) or not order_id.strip():
        return None, "ID 누락"
    if not isinstance(item, str) or not item.strip():
        return None, "상품명 누락"
    unit_price = positive_int(row.get("unit_price"))
    quantity = positive_int(row.get("quantity"))
    if unit_price is None:
        return None, "단가 오류"
    if quantity is None:
        return None, "수량 오류"
    clean = {
        "order_id": order_id.strip(),
        "item": item.strip(),
        "unit_price": unit_price,
        "quantity": quantity,
        "amount": unit_price * quantity,
    }
    return clean, None


def reject_record(index, row, reason):
    # 번호는 CSV 행 번호가 아니라 'CSV 목록 + JSON 목록'에서 1부터 센 순서입니다.
    # 원본 값을 함께 보관하여 왜 제외했는지 나중에 설명할 수 있게 합니다.
    return {"record_no": index, "reason": reason, "raw": row.copy()}
