"""실습 07~08 응용: 한 파일에서 회귀·분류 각각 세 후보를 비교합니다."""
from pathlib import Path
import pandas as pd

# 파일 경로 설정 및 원본 데이터를 불러와 request_id를 인덱스로 지정
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")

# 이 표는 전날의 분할 소속과 각 분할 내부의 행 순서(position)를 함께 보존합니다.
split = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = split.loc[split["split"] == "train"].sort_values("position")["request_id"]
valid_ids = split.loc[split["split"] == "valid"].sort_values("position")["request_id"]

# 복원된 ID를 바탕으로 원본 데이터에서 train과 valid 데이터셋 추출
train = raw.loc[train_ids]
valid = raw.loc[valid_ids]

# 모델 학습에 사용할 특성(features) 4가지 지정 (숫자형 2개, 범주형 2개)
features = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train = train[features]
X_valid = valid[features]

# test의 ID는 분할표에만 남겨 둡니다. test 입력·정답을 모델에 전달하지 않습니다.
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone

from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, precision_score, recall_score, f1_score, confusion_matrix

# 제공: 전날 만든 전처리입니다. 숫자 2열은 중앙값→표준화, 문자 2열은 최빈값→원핫입니다.
num = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
cat = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
pre = ColumnTransformer([("num", num, features[:2]), ("cat", cat, features[2:])])

# 제공 K: PPT 실습06의 동일 원본·분할·standard 탐색 결과(분류3, 회귀15)를 재사용합니다.
# 결과 저장을 위한 빈 리스트 초기화 (회귀 결과, 분류 결과, 전체 상세 예측값)
regression_rows = []
classification_rows = []
predictions = []

# 회귀(Regression) 모델 실험 영역 (목표: 실행시간 'elapsed_ms' 예측)
for name, estimator in [("Dummy", DummyRegressor()), ("Linear", LinearRegression()),
                        ("KNN15", KNeighborsRegressor(n_neighbors=15))]:
    # 전처리 파이프라인과 각 회귀 모델을 결합, 파이프라인 구성
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO A07r: 회귀 모델을 학습하고 valid 예측을 구하세요.
    # 힌트: 정답 열은 elapsed_ms입니다.
    # pass
    # prediction = None
    
    # 훈련 데이터의 입력과 정답으로 모델 학습 진행
    model.fit(X_train, train["elapsed_ms"])
    # 검증 데이터를 투입해 실행시간 예측값 생성
    prediction = model.predict(X_valid)

    # MAE 및 RMSE 회귀 평가 지표 계산 후 결과 목록에 추가 (값이 낮을수록 우수)
    regression_rows.append({"model": name, "scale": "standard",
        "MAE_ms": mean_absolute_error(valid["elapsed_ms"], prediction),
        "RMSE_ms": root_mean_squared_error(valid["elapsed_ms"], prediction)})

    # 시각화 및 상세 분석을 위해 예측 결과 상세 내역을 데이터프레임으로 변환하여 저장 목록에 추가
    predictions.append(pd.DataFrame({"request_id": valid.index, "task": "regression", "model": name,
        "actual": valid["elapsed_ms"].to_numpy(), "predicted": prediction}))

# 분류(Classification) 모델 실험 영역 (목표: 실패 여부 'failed' 예측)
for name, estimator in [("Dummy", DummyClassifier(strategy="most_frequent")),
                        ("Logistic", LogisticRegression(C=1.0, max_iter=1000)),
                        ("KNN3", KNeighborsClassifier(n_neighbors=3))]:
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO A07c: 분류 모델을 학습하고 valid 예측을 구하세요.
    # 힌트: 정답 열은 failed입니다.
    # pass
    # prediction = None
    model.fit(X_train, train["failed"])
    prediction = model.predict(X_valid)
    
    tn, fp, fn, tp = confusion_matrix(valid["failed"], prediction, labels=[0, 1]).ravel()
    classification_rows.append({"model": name, "scale": "standard",
        "F1": f1_score(valid["failed"], prediction, zero_division=0),
        "Precision": precision_score(valid["failed"], prediction, zero_division=0),
        "Recall": recall_score(valid["failed"], prediction, zero_division=0), "FP": fp, "FN": fn})
    predictions.append(pd.DataFrame({"request_id": valid.index, "task": "classification", "model": name,
        "actual": valid["failed"].to_numpy(), "predicted": prediction}))

regression = pd.DataFrame(regression_rows)
classification = pd.DataFrame(classification_rows)

# 결과물 저장할 outputs 폴더 생성
out = HERE / "outputs"
out.mkdir(exist_ok=True)

# 회귀 비교표, 분류 비교표, 전체 상세 예측 내역 각각 csv 파일로 안전하게 저장 (UTF-8 인코딩)
regression.to_csv(out / "regression_comparison.csv", index=False, encoding="utf-8-sig")
classification.to_csv(out / "classification_comparison.csv", index=False, encoding="utf-8-sig")
pd.concat(predictions, ignore_index=True).to_csv(out / "validation_predictions.csv", index=False, encoding="utf-8-sig")

# 최종 검증 결과 출력
print("회귀 / valid 20건")
print(regression.round(3).to_string(index=False))
print("분류 / valid 20건")
print(classification.round(3).to_string(index=False))
print("저장: outputs의 비교표 2개와 validation_predictions.csv")
print("test는 학습·변환·예측·평가하지 않았습니다.")
