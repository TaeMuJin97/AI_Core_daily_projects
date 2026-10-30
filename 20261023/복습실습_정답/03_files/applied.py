"""03 파일 응용: 결측·잘못된 수량·상품명 등을 제외 사유와 함께 기록합니다."""
from pathlib import Path
from storage import read_csv, read_json, save_results
from validation import check_row, reject_record

BASE = Path(__file__).resolve().parent


def clean_with_reasons(rows):
    """입력은 ID가 서로 다른 10행입니다. 반환: (정상 List, 제외 List)."""
    # 해설 D_A1: 행 검사 결과에 따라 정상 목록과 제외 이유 목록을 나누세요.
    clean = []
    rejected = []
    for index, row in enumerate(rows, start=1):
        checked, reason = check_row(row)
        if reason is not None:
            # 유효하지 않은 값을 0으로 채우지 않고 별도로 남깁니다.
            rejected.append(reject_record(index, row, reason))
        else:
            clean.append(checked)
    return clean, rejected


def group_by_item(rows):
    """정제된 행을 상품명별로 모아 {상품명: {quantity, amount}}로 반환합니다."""
    # 해설 D_A2: 상품별 수량과 금액을 Dictionary에 누적하세요.
    groups = {}
    for row in rows:
        item = row["item"]
        if item not in groups:
            groups[item] = {"quantity": 0, "amount": 0}
        groups[item]["quantity"] += row["quantity"]
        groups[item]["amount"] += row["amount"]
    return groups


def main():
    rows = read_csv(BASE / "data/orders_applied.csv") + read_json(BASE / "data/orders_applied.json")
    clean, rejected = clean_with_reasons(rows)
    summary = {"raw_count": len(rows), "accepted_count": len(clean),
               "rejected_count": len(rejected), "by_item": group_by_item(clean)}
    save_results(BASE / "outputs/applied", clean, summary, rejected)
    print("원본 / 정상 / 제외:", len(rows), len(clean), len(rejected))
    for item, values in summary["by_item"].items():
        print(item, values["quantity"], "개", values["amount"], "원")
    print("행 수 보존:", len(rows) == len(clean) + len(rejected))
    print("결과: 03_files/outputs/applied")

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
