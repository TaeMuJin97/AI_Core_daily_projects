"""실습 07~08 응용: 얕은 폴더 구조에서 분류 실험표를 완성합니다."""
from pathlib import Path
import pandas as pd

# 제공: 전날의 분할 소속뿐 아니라 position 순서까지 그대로 읽습니다.
# =========================================================
# 1. 데이터 로드 및 고정 분할 (Train / Valid) 복원
# =========================================================
# 원본 데이터(requests.csv) 로드
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")

# 분할 명세서(split_manifest.cdv)를 읽어 동일한 분할 소속 및 행 순서(position) 복원
manifest = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"]
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"]

train = raw.loc[train_ids]
valid = raw.loc[valid_ids]

# 실행 전에 알 수 있는 입력 특성(Features) 4개와 이진 분류 정답 분리 (failed: 0=성공, 1=실패)
FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train, X_valid = train[FEATURES], valid[FEATURES]
y_train, y_valid = train["failed"], valid["failed"]

# 결과물(csv) 저장할 outputs 폴더 생성 (test 사용 X)
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

# =========================================================
# 2. 트리·앙상블 모델을 위한 전처리 파이프라인 구성
# =========================================================
# test 20건의 입력·정답은 아래 모델에 전달하지 않습니다.
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import clone

# 제공: 전날 배운 결측 대체와 문자 변환입니다. 통계는 fit할 때만 배웁니다.
# 트리 기반 모델은 기준값 분기(Splitting) 방식이므로 수치형 변수의 표준화(Scaling)를 생략
# - 수치형 2열 (input_chars, allowed_tools): 결측치를 중앙값(median)으로 대체
# - 범주형 2열 (task_type, priority): 결측치를 최빈값(most_frequent)으로 대체 후 원핫 인코딩(미지 범주 무시=handle_unknown=ignore)
pre = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), FEATURES[:2]),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                      ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), FEATURES[2:]),
])

# 트리는 이 실습에서 표준화하지 않습니다. 각 후보·fold마다 새 전처리기를 학습합니다.
# =========================================================
# 3. 교차검증(CV) 설정 및 비교할 후보 모델(Candidates) 정의
# =========================================================
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score, confusion_matrix

# train(60건) 내부에서 실패(1) 비율을 유지하며 5등분(학습 48 / 평가 12)하는 고정 Fold 생성
folds = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=42).split(X_train, y_train))

# 사전 고정된 하이퍼파라미터로 비교한 4가지 분류 모델 후보군 정의
# 1) Dummy: 최빈 클래스로만 예측하는 기준선(Baseline) 모델
# 2) Tree: 최대 깊이=3, 잎 최소 샘플 3으로 과적합을 '제한'한 단일 결정 트리
# 3) Forest: 100개의 트리를 독립적으로 학습시켜 확률 평균으로 결합하는 배깅(Bagging) 앙상블
# 4) XGB: 88회차 동안 깊이 2의 트리로 이전 오차(Logloss)를 순차 보정하는 부스팅(Boosting) 앙상블

candidates = [("Dummy", DummyClassifier(strategy="most_frequent")),
              ("Tree", DecisionTreeClassifier(max_depth=3, min_samples_leaf=3, random_state=42)), ("Forest", RandomForestClassifier(n_estimators=100, max_depth=4, min_samples_leaf=2,
                                    max_features="sqrt", random_state=42, n_jobs=1)), ("XGB", XGBClassifier(n_estimators=80, max_depth=2, learning_rate=0.05,
                  subsample=0.8, colsample_bytree=1.0, reg_lambda=1.0,
                  objective="binary:logistic", eval_metric="logloss",
                  tree_method="hist", device="cpu", random_state=42, n_jobs=1))]

# =========================================================
# 4. 모델별 5-Fold 교차검증, 전체 Train 학습, Valid 진단 및 중요도 추출
# =========================================================
rows, cv_rows = [], []
predictions = pd.DataFrame({"request_id": X_valid.index, "actual": y_valid.to_numpy()})


for name, estimator in candidates:
    # 데이터 누수(Data Leakage)방지를 위해 각 후보/폴드마다 독립된 새 전처리기(clone)을 모델과 결합
    model = Pipeline([("pre", clone(pre)), ("model", estimator)])
    # TODO A07a: train 내부 교차검증 뒤 전체 train으로 학습하세요.
    
    # [Step 1] 아직 fit하지 않은 Pipeline 전체를 전달하여 각 fold의 학습 48건 안에서만 전처리·모델 학습 수행
    scores = cross_val_score(model, X_train, y_train, cv=folds, scoring="f1", n_jobs=1)
    
    # TODO 끝
    # TODO A07b: valid의 예측을 prediction에 넣으세요.
    # [Step 2] 교차검증 완료 후, train 60건 전체로 파이프라인을 최종 학습하고 valid 20건에 대해 예측 수행
    model.fit(X_train, y_train)
    prediction = model.predict(X_valid)
    # TODO 끝

    # [Step 3] 혼동 행렬(Confusion Matrix)을 통해 가짜 양성(FP)과 가짜 음성(FN) 오차 개수 추출
    tn, fp, fn, tp = confusion_matrix(y_valid, prediction, labels=[0, 1]).ravel()
    
    # 모델별 요약 성적표 기록(CV 평균/표준편차, Train F1, Valid F1, 오차 개수)
    rows.append({"model": name, "CV_F1": scores.mean(), "CV_std": scores.std(),
                 "train_F1": f1_score(y_train, model.predict(X_train), zero_division=0),
                 "valid_F1": f1_score(y_valid, prediction, zero_division=0), "FP": fp, "FN": fn})
    
    # 각 폴드(1~5회차)별 상세평가 점수 기록
    for number, value in enumerate(scores, start=1):
        cv_rows.append({"model": name, "fold": number, "fit_n": 48, "evaluate_n": 12, "F1": value})
    
    # 검증 데이터에 대한 모델별 예측값 '컬럼' 추가
    predictions[name] = prediction

    # [Step 4] Random Forest 모델인 경우, 전처리 후 생성된 8개 특성 이름과 불순도 기반 중요도(MDI)를 매칭하여 저장
    if name == "Forest":
        importance = pd.DataFrame({"feature": model["pre"].get_feature_names_out(),
                                   "importance": model["model"].feature_importances_})

# =========================================================
# 5. 실험 산출물 CSV 저장 및 요약 출력
# =========================================================
comparison = pd.DataFrame(rows)

# 4가지 핵심 실험 결과표를 outputs 폴더에 UTF-8(BOM 포함) 인코딩 저장
comparison.to_csv(OUT / "classification_comparison.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(cv_rows).to_csv(OUT / "cv_scores.csv", index=False, encoding="utf-8-sig")
predictions.to_csv(OUT / "validation_predictions.csv", index=False, encoding="utf-8-sig")
importance.to_csv(OUT / "feature_importance.csv", index=False, encoding="utf-8-sig")

# 최종 비교표 및 실험 원칙 출력
print(comparison.round(4).to_string(index=False))
print("CV 평균 F1 최대, 동률이면 미리 제시한 후보 순서로 선택합니다. valid는 별도 진단입니다.")
print("저장: outputs/classification_comparison.csv, cv_scores.csv, validation_predictions.csv, feature_importance.csv")
print("test는 학습·변환·예측·평가하지 않았습니다.")
