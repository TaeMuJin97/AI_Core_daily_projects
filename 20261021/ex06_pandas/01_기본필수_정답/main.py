"""PPT 51쪽의 합성 표. 원본 보존과 결측의 의미를 함께 확인합니다."""
from pathlib import Path
import json
import pandas as pd
from sample_data import RAW_RECORDS
BASE = Path(__file__).resolve().parent

def make_raw():
    # 해설 FRAME: 제공된 RAW_RECORDS로 DataFrame을 만드세요. 열 순서는 name,difficulty,score,role_count입니다.
    return pd.DataFrame(RAW_RECORDS, columns=["name", "difficulty", "score", "role_count"])

def select_applied(raw):
    # 해설 SELECT: 원본에서 difficulty가 '응용'인 행의 name을 List로 반환하세요. 중복 제거 전입니다.
    return raw.loc[raw["difficulty"] == "응용", "name"].tolist()

def clean_data(raw):
    # 해설 CLEAN: 완전 중복 제거→copy→점수 숫자 변환(coerce)→난이도 결측을 '미정'으로 처리하세요.
    cleaned = raw.drop_duplicates().copy()
    cleaned["score"] = pd.to_numeric(cleaned["score"], errors="coerce")
    cleaned["difficulty"] = cleaned["difficulty"].fillna("미정")
    return cleaned

def group_means(cleaned):
    # 해설 MEANS: 정제한 표를 난이도로 묶고 score 평균 Series를 반환하세요. 처음 나타난 순서를 유지하세요.
    return cleaned.groupby("difficulty", sort=False)["score"].mean()

def group_summary(cleaned):
    # 해설 AGG: difficulty별 total(size)·valid(count)·mean_score(mean)을 한 표로 만들고 인덱스를 열로 바꾸세요.
    return cleaned.groupby("difficulty", sort=False).agg(
        total=("score", "size"), valid=("score", "count"), mean_score=("score", "mean")
    ).reset_index()

def audit_changes(raw, cleaned):
    # 해설 AUDIT: 원본/정제 행 수, 제거 중복, 원래 점수 결측, 숫자 변환 실패, 정제 점수 결측, 채운 난이도 수를 기록하세요.
    deduplicated = raw.drop_duplicates()
    numeric = pd.to_numeric(deduplicated["score"], errors="coerce")
    # 원래 결측과 '미정'처럼 값은 있었으나 변환에 실패한 경우를 구분합니다.
    invalid = deduplicated["score"].notna() & numeric.isna()
    return {"before_rows": len(raw), "after_rows": len(cleaned),
            "removed_duplicates": len(raw) - len(deduplicated),
            "original_score_missing": int(deduplicated["score"].isna().sum()),
            "numeric_failures": int(invalid.sum()),
            "clean_score_missing": int(cleaned["score"].isna().sum()),
            "filled_difficulty": int(deduplicated["difficulty"].isna().sum())}

def report_three_sentences(audit):
    """제공 출력 형식. 심화에서는 숫자의 근거를 설명할 수 있어야 합니다."""
    return (f"원본 {audit['before_rows']}행을 보존하고 완전 중복 {audit['removed_duplicates']}행을 제거해 {audit['after_rows']}행을 얻었습니다.\n"
            f"원래 점수 결측 {audit['original_score_missing']}개와 숫자 변환 실패 {audit['numeric_failures']}개를 구분했으며, 점수 결측 {audit['clean_score_missing']}개를 0으로 채우지 않았습니다.\n"
            f"난이도 결측 {audit['filled_difficulty']}개는 미정으로 표시했고, 평균은 유효 점수 개수와 함께 해석합니다.\n")

def json_records(frame):
    """제공 출력 도구: JSON의 표준 값 null로 결측을 저장합니다. Pandas 내부에서는 NaN을 유지합니다."""
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")

def write_json(name, value):
    path = BASE / "outputs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")

def main():
    raw = make_raw()
    snapshot = raw.copy(deep=True)
    print("shape:", raw.shape)
    print("columns:", raw.columns.tolist())
    print("응용 name:", select_applied(raw))

    print("원본 보존:", raw.equals(snapshot))

if __name__ == "__main__":
    main()
