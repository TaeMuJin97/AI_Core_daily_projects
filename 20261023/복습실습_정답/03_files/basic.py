"""03 파일 기본필수: 정상 주문 5건. 읽기 → 공백/자료형 정제 → 집계 → 저장."""
from pathlib import Path
from storage import read_csv, read_json, save_results

BASE = Path(__file__).resolve().parent


def load_orders(csv_path, json_path):
    """CSV 주문 List와 JSON 주문 List를 순서대로 합칩니다."""
    # 해설 D_B1: CSV와 JSON을 각각 읽어 두 주문 목록을 연결하세요.
    # 두 파일의 주문은 서로 다른 거래입니다. 같은 주문의 다른 형식 사본이 아닙니다.
    csv_rows = read_csv(csv_path)
    json_rows = read_json(json_path)
    return csv_rows + json_rows


def clean_one(row):
    """정상 입력 1행 → amount가 추가된 새 Dict. 원본은 변경하지 않습니다."""
    # 해설 D_B2: 문자열 공백을 없애고 숫자를 정수로 바꾸어 새 행을 반환하세요.
    # 기본필수의 단가·수량은 모두 정상 입력입니다. 잘못된 값은 응용에서 다룹니다.
    order_id = row["order_id"].strip()
    item = row["item"].strip()
    unit_price = int(row["unit_price"])
    quantity = int(row["quantity"])
    # 원본 row를 직접 고치지 않고 새 Dictionary를 만듭니다.
    return {
        "order_id": order_id,
        "item": item,
        "unit_price": unit_price,
        "quantity": quantity,
        "amount": unit_price * quantity,
    }


def make_summary(rows):
    """정제된 List를 입력받아 건수·수량·금액을 담은 Dict를 반환합니다."""
    # 해설 D_B3: 정제된 주문의 건수·수량 합·금액 합을 반환하세요.
    quantity = 0
    amount = 0
    for row in rows:
        quantity = quantity + row["quantity"]
        amount = amount + row["amount"]
    return {"order_count": len(rows), "total_quantity": quantity, "total_amount": amount}


def main():
    rows = load_orders(BASE / "data/orders_basic.csv", BASE / "data/orders_basic.json")
    clean = []
    for row in rows:
        clean.append(clean_one(row))
    summary = make_summary(clean)
    save_results(BASE / "outputs/basic", clean, summary)
    print("원본 주문:", len(rows))
    print("정제 주문:", summary["order_count"])
    print("상품 수량:", summary["total_quantity"])
    print("전체 금액:", summary["total_amount"])
    print("저장·재읽기: 확인 완료")
    print("결과: 03_files/outputs/basic")

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
