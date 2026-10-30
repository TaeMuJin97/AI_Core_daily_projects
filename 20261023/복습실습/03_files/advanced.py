"""03 파일 심화(선택): 중복 ID와 품질 기록. CSV+JSON 14행을 처리합니다."""
from pathlib import Path
from storage import read_csv, read_json, save_results
from validation import check_row, reject_record

BASE = Path(__file__).resolve().parent


def clean_unique(rows):
    """첫 유효 행 유지, 뒤의 같은 ID는 보류. 실제 업무에서는 담당자 확인이 필요합니다."""
    # TODO D_D1: 유효성 검사 후 중복 ID를 보류하고 첫 유효 행만 유지하세요.
    raise NotImplementedError("D_D1: 유효성 검사 후 중복 ID를 보류하고 첫 유효 행만 유지하세요.")


def count_reasons(rejected):
    """반환: {제외 이유: 건수}. 이유가 있는 모든 행을 빠짐없이 셉니다."""
    # TODO D_D2: 제외 이유별 건수를 집계하세요.
    raise NotImplementedError("D_D2: 제외 이유별 건수를 집계하세요.")


def main():
    rows = read_csv(BASE / "data/orders_advanced.csv") + read_json(BASE / "data/orders_advanced.json")
    clean, rejected = clean_unique(rows)
    total = 0
    for row in clean:
        total += row["amount"]
    summary = {"raw_count": len(rows), "accepted_count": len(clean),
               "rejected_count": len(rejected), "total_amount": total,
               "reason_counts": count_reasons(rejected)}
    save_results(BASE / "outputs/advanced", clean, summary, rejected)
    print("원본 / 정상 / 제외:", len(rows), len(clean), len(rejected))
    print("전체 금액:", total)
    print("이유별 건수:", summary["reason_counts"])
    print("행 수 보존:", len(rows) == len(clean) + len(rejected))
    print("결과: 03_files/outputs/advanced")

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
