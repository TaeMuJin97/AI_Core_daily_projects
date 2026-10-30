"""실습 05 응용: train 수치2열만 결측 대체·표준화하여 K=3으로 묶습니다."""
from pathlib import Path
import pandas as pd
import numpy as np

# 1. 고정 분할(train/valid) 복원 및 수치형(NUM)·범주형(CAT) 컬럼명 분리
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
manifest = pd.read_csv(HERE / "data/split_manifest.csv")

train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"].tolist()
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"].tolist()
train, valid = raw.loc[train_ids].copy(), raw.loc[valid_ids].copy()

FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
NUM, CAT = FEATURES[:2], FEATURES[2:] # NUM = ["input_chars", "allowed_tools"]
X_train, X_valid = train[FEATURES].copy(), valid[FEATURES].copy()
y_train, y_valid = train["failed"], valid["failed"]

OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# =====================================================================
# 2. K-Means 군집화 파이프라인 구성 및 비지도 학습
# =====================================================================
# [핵심 학습 1] 왜 K-Means 앞에 Imputer와 StandardScaler가 필수인가요?
# - K-Means는 각 데이터와 군집 중심(Centroid) 사이의 '유클리드 거리'를 계산해 묶는 알고리즘입니다.
# - 글자 수(수백~수천 단위)와 도구 수(1~5 단위)를 그대로 넣으면 글자 수 차이가 거리를 지배해버리므로,
#   반드시 결측치를 채운 뒤(median) 두 변수의 단위를 동등하게 맞추는 표준화(StandardScaler)를 거쳐야 합니다.
# - n_init=10: 초기 중심점 위치를 다르게 잡아 10번 반복 실행한 뒤, 가장 촘촘하게 묶인(inertia가 가장 작은) 결과를 선택합니다.
cluster = Pipeline([("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("kmeans", KMeans(n_clusters=3, n_init=10, random_state=42))])

# [핵심 학습 2] 비지도학습(Unsupervised Learning)의 fit
# - 지도학습과 달리 정답(y_train)을 전달하지 않고 오직 수치형 입력 2열(X_train[NUM])만 넣어 패턴을 찾습니다.
# - 또한 평가 데이터 누수를 막기 위해 전체 100건이 아닌 'train 60건'만으로 군집 중심을 학습합니다.
# TODO A05: 수치2열만으로 cluster를 학습하세요. failed나 elapsed_ms를 넣지 않습니다.
cluster.fit(X_train[NUM])
# TODO 끝

# =====================================================================
# 3. 군집 라벨 추출, 실루엣 점수용 변환, 원단위 중심 좌표 복원
# =====================================================================
# 학습된 KMeans 단계에서 train 60건 각각이 배정받은 군집 번호(0, 1, 2) 배열을 꺼냅니다.
labels = cluster["kmeans"].labels_

# [핵심 학습 3] 파이프라인 슬라이싱: cluster[:-1].transform(...)
# - 파이프라인에 리스트 슬라이싱([:-1])을 쓰면 마지막 단계("kmeans")만 쏙 빼고
#   앞의 전처리 단계("imputer" -> "scaler")까지만 통과시킨 '표준화된 좌표 배열(z)'을 얻을 수 있습니다.
# - 실루엣 점수(silhouette_score)는 K-Means가 실제로 거리를 계산했던 '표준화 공간(z)' 위에서 측정해야 정확합니다.
z = cluster[:-1].transform(X_train[NUM])

# [핵심 학습 4] 표준화된 중심 좌표를 원래 단위로 되돌리기: inverse_transform(...)
# - cluster["kmeans"].cluster_centers_ 에는 표준화된 상태(평균 0, 표준편차 1 기준)의 중심 좌표가 들어 있어 사람이 직관적으로 읽기 어렵습니다.
# - scaler의 .inverse_transform()에 이 좌표를 넣으면 "평균 몇 글자, 도구 몇 개"인지 원래 단위(원단위)로 역변환해 줍니다!
centers = cluster["scaler"].inverse_transform(cluster["kmeans"].cluster_centers_)


profile = pd.DataFrame(centers, columns=NUM)
profile.insert(0, "cluster", range(3))

# [핵심 학습 5] np.bincount(labels, minlength=3)으로 군집별 데이터 개수 세기
# - 0번, 1번, 2번 군집에 각각 몇 건의 데이터가 속했는지 빈도수를 순서대로 세어줍니다 (결과: 24, 19, 17).
# - minlength=3은 혹시 특정 군집에 데이터가 0건이더라도 길이가 3인 배열을 유지하도록 보장하는 안전장치입니다.
profile["n"] = np.bincount(labels, minlength=3)
profile.to_csv(OUT / "cluster_profile.csv", index=False, encoding="utf-8-sig")
pd.DataFrame({"request_id": train_ids, "cluster": labels}).to_csv(OUT / "cluster_assignments.csv", index=False, encoding="utf-8-sig")
print(profile.round(3).to_string(index=False))

# [핵심 학습 6] silhouette_score(z, labels) 해석
# - 같은 군집끼리는 얼마나 가깝고 다른 군집과는 얼마나 멀리 떨어져 있는지(-1 ~ 1 사이, 클수록 분리도 우수) 계산합니다.
print("silhouette(표준화 공간):", round(silhouette_score(z, labels), 3))

# [오늘의 메인 교훈]
# 군집 0, 1, 2는 입력 특성(글자 수, 도구 수)이 비슷한 것끼리 묶어 붙인 '이름표'일 뿐입니다.
# 0번이 성공이고 1번이 실패라거나, 2번이 더 위험하다는 식의 순서·우열 의미는 전혀 없습니다.
print("군집 번호에는 실패·성공·우열의 뜻이 없습니다.")
