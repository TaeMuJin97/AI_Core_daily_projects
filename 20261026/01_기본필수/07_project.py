"""실습 07~08 기본필수: 같은 파일을 완성하고 다시 실행합니다."""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

# 제공: 이 파일 옆의 CSV를 읽고, 전날과 같은 요청들을 12 / 4 / 4로 나눕니다.
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "requests.csv")

# 전체 데이터 중 20%를 test로 떼어놓고, 나머지 80%중 25%를 valid로 나눕니다. 자연스럽게 나머지 75%가 train이 됩니다.
develop, test = train_test_split(raw, test_size=0.2, random_state=42, stratify=raw["failed"])
train, valid = train_test_split(develop, test_size=0.25, random_state=42, stratify=develop["failed"])
# test는 보관만 합니다. 학습·예측에 넣지 않습니다.

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.base import clone
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, f1_score

# 제공: 전날의 두 입력을 그대로 사용합니다. elapsed_ms와 failed는 정답이므로 입력에서 뺍니다.
features = ["input_chars", "task_type"]
X_train = train[features]
X_valid = valid[features]

# 열별 전처리 방식 정의: 숫자형은 표준화(standardScaler), 범주형은 원핫 인코딩(OneHotEncoder) 수행
pre = ColumnTransformer([
    ("num", StandardScaler(), ["input_chars"]),
    ("cat", OneHotEncoder(sparse_output=False), ["task_type"]),
])
# 제공: 아래 두 반복은 같은 구조입니다. 첫 번째는 숫자, 두 번째는 클래스 정답을 사용합니다.
# 결과 저장을 위한 빈 리스트와 검증 결과 데이터프레임 초기화
regression_rows = []
classification_rows = []
result = valid[["request_id", "elapsed_ms", "failed"]].copy()
# 1. 회귀(Regression) 모델 실험 영역 (목표: 실행시간 'elapsed_ms' 예측)
for name, estimator in [("Dummy", DummyRegressor()), ("Linear", LinearRegression())]:
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO B07a: 실행시간 elapsed_ms로 학습하고 X_valid를 예측하세요.
    # 힌트: model.fit(X_train, train["elapsed_ms"]) 다음 predict(X_valid)를 연결합니다.
    # pass
    # prediction = None
    model.fit(X_train, train["elapsed_ms"])
    prediction = model.predict(X_valid)
    regression_rows.append({"model": name, "MAE_ms": mean_absolute_error(valid["elapsed_ms"], prediction)})
    result[name + "_ms"] = prediction

# 2. 분류(Classification) 모델 실험 영역 (목표: 실패 여부 'failed' 예측)
for name, estimator in [("Dummy", DummyClassifier(strategy="most_frequent")),
                        ("Logistic", LogisticRegression(max_iter=1000))]:
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO B07b: 실패 여부 failed로 학습하고 X_valid를 예측하세요.
    # # 힌트: 회귀와 같은 흐름이며 정답 열만 failed로 바뀝니다.
    # pass
    # prediction = None
    model.fit(X_train, train["failed"])
    prediction = model.predict(X_valid)

    classification_rows.append({"model": name, "F1": f1_score(valid["failed"], prediction, zero_division=0)})
    result[name + "_failed"] = prediction

# 제공: 두 종류의 지표를 섞지 않고 별도 표로 저장합니다. 저장 코드는 수정하지 않아도 됩니다.
# 3. 결과 정리 및 CSV 파일 저장 영역
regression = pd.DataFrame(regression_rows)
classification = pd.DataFrame(classification_rows)
regression.to_csv(HERE / "regression_comparison.csv", index=False, encoding="utf-8-sig")
classification.to_csv(HERE / "classification_comparison.csv", index=False, encoding="utf-8-sig")
result.to_csv(HERE / "validation_predictions.csv", index=False, encoding="utf-8-sig")
print("분할:", len(train), len(valid), len(test))
print("회귀 비교 / 낮은 MAE가 좋음")
print(regression.round(3).to_string(index=False))
print("분류 비교 / 높은 F1이 좋음")
print(classification.round(3).to_string(index=False))
print("저장: regression_comparison.csv, classification_comparison.csv, validation_predictions.csv")
print("test는 학습·예측하지 않았습니다.")
