"""실습 05 응용: PPT와 같은 XGBoost 80회차 분류 모델입니다."""
from pathlib import Path
import pandas as pd

# 제공: 전날의 분할 소속뿐 아니라 position 순서까지 그대로 읽습니다.
# 1. 파일 경로 설정 및 원본 데이터 불러와서 request_id를 인덱스로 지정
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
# 2. 전날 저장된 분할 명세서(split_manifest.csv)를 읽어 train과 valid의 ID 순서를 정확히 복원
manifest = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"]
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"]
train = raw.loc[train_ids]
valid = raw.loc[valid_ids]
# 3. 모델 학습에 사용할 특성(Features)과 정답(Target) 데이터 분리 지정
FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train, X_valid = train[FEATURES], valid[FEATURES]
y_train, y_valid = train["failed"], valid["failed"]
# 결과물 저장 폴더 생성
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
# test 20건의 입력·정답은 아래 모델에 전달하지 않습니다.
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone

# 제공: 전날 배운 결측 대체와 문자 변환입니다. 통계는 fit할 때만 배웁니다.
# 4. 전처리 파이프라인 정의 (트리 기반 모델은 표준화 생략)
pre = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), FEATURES[:2]),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), FEATURES[2:]),
])
# 트리는 이 실습에서 표준화하지 않습니다. 각 후보·fold마다 새 전처리기를 학습합니다.

from xgboost import XGBClassifier
from sklearn.metrics import f1_score, confusion_matrix, log_loss

# xgboost 분류기 모델 객체 생성 (하이퍼파라미터 설정)
estimator = XGBClassifier(n_estimators=80, max_depth=2, learning_rate=0.05,
                  subsample=0.8, colsample_bytree=1.0, reg_lambda=1.0,
                  objective="binary:logistic", eval_metric="logloss",
                  tree_method="hist", device="cpu", random_state=42, n_jobs=1)
model = Pipeline([("pre", clone(pre)), ("model", estimator)])
# TODO A05: Pipeline을 학습하고 valid를 예측하세요.
# 7. TODO 해결: 파이프라인 학습 및 검증 데이터 예측 수행
# 훈련 데이터 이용해 전처리와 모델 학습 동시에 진행 
model.fit(X_train, y_train)
# 검증 데이터 투입해 실패 여부(0 또는 1) 예측값 생성
prediction = model.predict(valid)
# TODO 끝

# 모델의 확률 예측값 추출 및 상세 평가 지표 계산
probability = model.predict_proba(X_valid)[:, 1]  # classes_ = [0, 1] 확인 후 실패1의 열 사용
print("클래스 순서:", model.classes_.tolist())
tn, fp, fn, tp = confusion_matrix(y_valid, prediction, labels=[0, 1]).ravel()
result = pd.DataFrame([{"train_F1": f1_score(y_train, model.predict(X_train), zero_division=0),
                       "valid_F1": f1_score(y_valid, prediction, zero_division=0), "FP": fp, "FN": fn,
                       "valid_logloss": log_loss(y_valid, probability, labels=[0, 1])}])
result.to_csv(OUT / "05_xgboost.csv", index=False, encoding="utf-8-sig")
print(result.round(3).to_string(index=False))
print("objective는 학습 목적, logloss는 진단용, 후보 비교의 주 지표는 F1입니다.")
