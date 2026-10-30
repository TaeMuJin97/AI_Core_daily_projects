"""프로젝트 시작점. 기본실행: python main.py / 선택: python main.py applied 또는 advanced"""
from pathlib import Path
import sys
from models import Order
from cleaning import clean_orders, clean_orders_advanced
from reporting import summarize_orders, group_orders
from storage import read_csv, read_json, save_results

BASE = Path(__file__).resolve().parent


def make_orders(rows):
    """정제된 Dict List를 Order 객체 List로 바꿉니다."""
    # TODO P_B3: 정제된 Dictionary마다 Order 객체를 만들어 목록에 담으세요.
    raise NotImplementedError("P_B3: 정제된 Dictionary마다 Order 객체를 만들어 목록에 담으세요.")


def run(mode="basic"):
    if mode not in ("basic", "applied", "advanced"):
        raise ValueError("모드는 basic, applied, advanced 중 하나입니다.")
    # 프로젝트 응용은 정상 5행에 상품별 집계만 추가합니다.
    # 03_files/applied의 불량 10행과 구분하세요.
    data_mode = "advanced" if mode == "advanced" else "basic"
    rows = read_csv(BASE / f"data/orders_{data_mode}.csv")
    rows = rows + read_json(BASE / f"data/orders_{data_mode}.json")
    if mode == "advanced":
        clean, rejected = clean_orders_advanced(rows)
    else:
        clean = clean_orders(rows)
        rejected = []
    orders = make_orders(clean)
    summary = summarize_orders(orders)
    summary["raw_count"] = len(rows)
    summary["rejected_count"] = len(rejected)
    if mode != "basic":
        summary["by_item"] = group_orders(orders)
    # 파일 저장용 Dict로 다시 꺼냅니다. Order 객체 자체는 JSON에 바로 저장하지 않습니다.
    saved_rows = []
    for order in orders:
        saved_rows.append(order.to_dict())
    save_results(BASE / "outputs" / mode, saved_rows, summary, rejected)
    return summary


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "basic"
    summary = run(mode)
    print("모드:", mode)
    print("원본 / 정상 / 제외:", summary["raw_count"], summary["order_count"], summary["rejected_count"])
    print("상품 수량:", summary["total_quantity"])
    print("전체 금액:", summary["total_amount"])
    print("저장·재읽기: 확인 완료")
    print("결과: 04_project/outputs/" + mode)


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("기본필수는 P_B1, P_B2, P_B3만 채우면 됩니다.")
        raise SystemExit(2)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("[입력 또는 저장 확인]", error)
        print("원본은 data, 생성 결과는 outputs 폴더입니다. 오류를 숨기고 계속 진행하지 않습니다.")
        raise SystemExit(1)
