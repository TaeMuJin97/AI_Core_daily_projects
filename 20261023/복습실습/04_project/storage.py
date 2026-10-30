"""제공 코드: 파일 여닫기와 저장. 이번 복습에서는 수정하지 않아도 됩니다."""
from pathlib import Path
import csv
import json

FIELDS = ["order_id", "item", "unit_price", "quantity"]
CLEAN_FIELDS = FIELDS + ["amount"]


def read_csv(path):
    # utf-8-sig는 BOM이 있는 CSV와 없는 UTF-8 CSV를 모두 읽습니다.
    # newline=""는 csv 모듈이 줄바꿈을 처리하게 합니다.
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("CSV 필수 열이 없습니다: " + ", ".join(FIELDS))
        rows = list(reader)
    return rows


def read_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = json.load(file)
    # 이번 입력 계약은 '주문 Dictionary의 List'입니다.
    # 잘못된 파일을 빈 목록으로 바꾸어 성공한 것처럼 보이게 하지 않습니다.
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("주문 JSON은 Dictionary들의 List여야 합니다.")
    return rows


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CLEAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        # 한글을 그대로 읽을 수 있게 저장하고, 들여쓰기로 구조를 보여 줍니다.
        json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.write("\n")


def save_results(output_dir, clean, summary, rejected=None):
    """입력과 다른 outputs 아래에 저장한 뒤 값과 자료형을 다시 확인합니다."""
    output_dir = Path(output_dir)
    write_csv(output_dir / "clean_orders.csv", clean)
    write_json(output_dir / "summary.json", summary)
    if rejected is not None:
        write_json(output_dir / "rejected.json", rejected)
    # CSV에서 읽은 숫자는 다시 문자열입니다. 숫자로 바꾼 후 원래 값과 비교합니다.
    restored = read_csv(output_dir / "clean_orders.csv")
    for row in restored:
        for field in ("unit_price", "quantity", "amount"):
            row[field] = int(row[field])
    with (output_dir / "summary.json").open(encoding="utf-8") as file:
        restored_summary = json.load(file)
    if restored != clean or restored_summary != summary:
        raise ValueError("저장 전후 값이 다릅니다. 결과 파일을 확인하세요.")
    return True
