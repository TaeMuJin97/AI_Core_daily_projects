"""정제 담당 모듈. 파일을 읽거나 화면에 출력하지 않고 값만 돌려줍니다."""
from validation import check_row, reject_record


def clean_orders(rows):
    """기본·응용 프로젝트용. 제공된 정상 주문 5행을 새 List로 반환합니다."""
    # 해설 P_B1: 정상 원본 행을 공백·숫자 정제한 새 목록으로 반환하세요.
    clean = []
    for row in rows:
        # 오후 실습의 clean_one 내용을 함수로 옮깁니다.
        unit_price = int(row["unit_price"])
        quantity = int(row["quantity"])
        clean.append({
            "order_id": row["order_id"].strip(),
            "item": row["item"].strip(),
            "unit_price": unit_price,
            "quantity": quantity,
            "amount": unit_price * quantity,
        })
    return clean


def clean_orders_advanced(rows):
    """선택 심화용. (정상 List, 제외 List)를 반환합니다."""
    # 해설 P_D1: 잘못된 행과 중복 ID를 이유와 함께 분리하세요.
    clean = []
    rejected = []
    seen_ids = set()
    for index, row in enumerate(rows, start=1):
        checked, reason = check_row(row)
        if reason is not None:
            rejected.append(reject_record(index, row, reason))
            continue
        if checked["order_id"] in seen_ids:
            rejected.append(reject_record(index, row, "중복 ID: 확인 필요"))
            continue
        seen_ids.add(checked["order_id"])
        clean.append(checked)
    return clean, rejected
