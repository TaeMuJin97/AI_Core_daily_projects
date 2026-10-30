"""실습 06 응용: 분류의 train F1과 valid F1을 기록합니다."""
from pathlib import Path
import pandas as pd

# 1. 파일 경로 설정 및 원본 데이터 불러오기 (request_id를 인덱스로 지정)
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
# 이 표는 전날의 분할 소속과 각 분할 내부의 행 순서(position)를 함께 보존합니다.
# 2. 전날 저장된 분할 명세서(split_manifest.csv)를 읽어 train과 valid의 ID 순서를 정확히 복원
split = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = split.loc[split["split"] == "train"].sort_values("position")["request_id"]
valid_ids = split.loc[split["split"] == "valid"].sort_values("position")["request_id"]

# 3. 복원된 ID를 바탕으로 원본 데이터에서 train과 valid 데이터셋 추출
train = raw.loc[train_ids]
valid = raw.loc[valid_ids]

# 사용할 특성(features) 4가지 지정 (숫자 2열, 문자 2열)
features = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train = train[features]
X_valid = valid[features]
# test의 ID는 분할표에만 남겨 둡니다. test 입력·정답을 모델에 전달하지 않습니다.
# test 데이터는 평가 누수를 막기 위해 모델 학습 및 예측 과정에서 완전히 배제합니다.

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score

# 4. 전처리 파이프라인 정의
# 숫자형 특성(앞의 2개): 결측치를 중간값(median)으로 채우고 표준화(StandardScaler) 수행
# 제공: 전날 만든 전처리입니다. 숫자 2열은 중앙값→표준화, 문자 2열은 최빈값→원핫입니다.
num = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
# 범주형 특성(뒤의 2개): 결측치를 최빈값(most_frequent)으로 채우고 원핫 인코딩(OneHotEncoder) 수행
cat = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
# ColumnTransformer를 통해 숫자형과 범주형 전처리를 각각 지정된 열에 결합
pre = ColumnTransformer([("num", num, features[:2]), ("cat", cat, features[2:])])

# 5. K값을 바꾸어가며 모델 성능을 비교하기 위한 반복문 실행
rows = []
for k in [1, 3, 5, 9, 15]:
    # TODO A06: n_neighbors를 반복 변수 k로 바꾸세요.
    # 힌트: K만 바꾸고 전처리와 분할은 고정합니다.
    # clone(pre)을 사용해 매 반복마다 초기화된 전처리 파이프라인을 사용하고, K값만 변경
    model = Pipeline([("pre", clone(pre)), ("model", KNeighborsClassifier(n_neighbors=k))])
    # 훈련 데이터로 전처리 및 모델 학습 진행
    model.fit(X_train, train["failed"])
    # 학습 데이터와 검증 데이터 각각에 대해 F1 점수를 측정하여 기록
    rows.append({"K": k,
        "train_F1": f1_score(train["failed"], model.predict(X_train), zero_division=0),
        "valid_F1": f1_score(valid["failed"], model.predict(X_valid), zero_division=0)})
# 6. 실험 결과를 데이터프레임으로 변환
comparison = pd.DataFrame(rows)
# 동점이면 작은 K: valid_F1 내림차순, K 오름차순으로 정렬합니다.
# 7. 최적의 K 선정 (조건: valid_F1 내림차순 정렬 우선, 점수가 같으면 K 오름차순 정렬 후 가장 위 행 선택)
best = comparison.sort_values(["valid_F1", "K"], ascending=[False, True]).iloc[0]
# 8. 결과물 저장 폴더 생성 및 CSV 파일로 저장
out = HERE / "outputs"
out.mkdir(exist_ok=True)

comparison.to_csv(out / "knn_search.csv", index=False, encoding="utf-8-sig")
# 9. 결과 출력
print(comparison.round(3).to_string(index=False))
print("선택 K:", int(best["K"]))
print("저장: outputs/knn_search.csv")
