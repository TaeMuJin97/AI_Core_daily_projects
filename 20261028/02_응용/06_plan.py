"""실습 06 응용: 04번에서 만든 CV 표만 읽어 선택하고 평가 계획을 기록합니다."""
from pathlib import Path
import pandas as pd
import json

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"

# 먼저 04_features.py를 완료하세요. valid_F1을 이용해 후보를 재선택하지 않습니다.
# 04번 실습에서 저장해 둔 기본 모델 vs 파생 특성 추가 모델의 비교표를 불러옵니다.
table = pd.read_csv(OUT / "feature_comparison.csv")

# =====================================================================
# 1. TODO A06 해결: CV_F1 최댓값 기준으로 최종 모델 자동 선택하기
# =====================================================================
# [핵심 학습 1] .idmax()로 최고 점수 행의 모델 이름 뽑아내기
# -table["CVF1"].idxmax()는 "CV_F1" 열에서 값이 가장 큰(max값) 행의 인덱스 번호를 찾아줍니다.
# -만약 두 후보의 점수가 소수점 끝까지 완전히 똑같다면(동점), .idxmax()는 자동으로 '맨 처음 등장한 행'의 인덱스를 반환하므로
# "정확한 동점은 표의 첫 후보를 사용한다"는 조건까지 한 줄로 완벽하게 해결됩니다.
# - (참고: sort_values("CV_F1", ascending=False, kind="mergesort").iloc[0]["model"] 로 작성해도 동일하게 동작합니다.)
# - ★주의★ valid_F1은 개발 중 진단용일 뿐이므로, 모델 선택 기준은 오직 train 내부 교차검증 점수인 'CV_F1'만 사용합니다.
# TODO A06: CV_F1이 가장 큰 행의 model 이름을 선택하세요. 정확한 동점은 표의 첫 후보를 사용합니다.
# selected = "Logistic"
selected = table.loc[table["CV_F1"].idxmax(), "model"]
# TODO 끝

# =====================================================================
# 2. 데이터 분할 ID 복원 및 평가 계획(Plan) 딕셔너리 구성
# =====================================================================
manifest = pd.read_csv(HERE / "data/split_manifest.csv")

# [핵심 학습 2] 딕셔너리 컴프리헨션(Dictionary Comprehension)으로 분할 ID 묶기
# - for문을 한 줄로 압축하여 {"train": [ID목록...], "valid": [ID목록...], "test": [ID목록...]} 형태의 딕셔너리를 만듭니다.
# - 각 분할 내부의 원래 행 순서(position)가 절대 섞이지 않도록 .sort_values("position")으로 정렬한 뒤 리스트(.tolist())로 변환합니다.
ids = {name: manifest.loc[manifest["split"] == name].sort_values("position")["request_id"].tolist()
       for name in ["train", "valid", "test"]}

# [핵심 학습 3] 평가 설정 동결(Freeze)을 위한 메타데이터 구성
# - test 데이터를 열어보기 전에 "무엇을, 어떤 기준으로 평가할지" 모든 규칙을 박제해 둡니다.
# - "derived": selected == "Logistic_FE" 
#   -> 선택된 이름이 "Logistic_FE"이면 True(파생 변수 사용), 아니면 False(미사용)가 자동으로 들어가는 깔끔한 불리언 비교식입니다.
plan = {"selected": selected, "C": 1, "max_iter": 1000,
        "features": ["input_chars", "allowed_tools", "task_type", "priority"],
        "derived": selected == "Logistic_FE", "threshold": 0.5,
        "rule": "score > threshold", "positive_label": 1,
        "selection": "train60 5-fold mean F1; exact tie: Logistic first", "split_ids": ids}

# =====================================================================
# 3. JSON 파일로 저장하여 설정 잠금(Lock) 완료
# =====================================================================
# [핵심 학습 4] json.dumps()와 Path.write_text()로 JSON 파일 저장하기
# - json.dumps(plan, ...): 파이썬 딕셔너리(plan)를 JSON 포맷의 '문자열(String)'로 변환합니다.
#   1) ensure_ascii=False: 한글이 깨지지 않고(유니코드 기호 \uXXXX로 바뀌지 않고) 그대로 저장되게 합니다.
#   2) indent=2: 줄바꿈과 2칸 들여쓰기를 적용해 사람이 열어봤을 때 읽기 예쁘게 정렬해 줍니다.
# - .write_text(..., encoding="utf-8"): 변환된 JSON 문자열을 selection.json 파일로 단번에 기록합니다.
(OUT / "selection.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

print("선택:", selected)
print("설정: C=1 / 임계값 0.5 초과 / 개발80으로 재학습 / test20 최종 확인")

# [오늘의 메인 교훈]
# 일단 이 selection.json이 만들어지고 나면(동결), 이후 test 점수가 예상보다 낮게 나오더라도
# 다시 돌아와서 모델이나 임계값(0.5)을 고치는 '재선택(컨닝)'을 해서는 절대 안 됩니다!
print("저장: outputs/selection.json (최종평가 이후 변경하지 않습니다.)")
