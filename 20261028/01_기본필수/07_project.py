"""실습 07~08: 06번의 설정을 그대로 읽어 개발 16건으로 학습하고 test 4건을 최종 평가합니다."""
from pathlib import Path
import pandas as pd
import numpy as np
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

HERE = Path(__file__).resolve().parent

# 제공: 06번을 먼저 완료하세요. 이 프로그램은 CV·설정 선택을 다시 하지 않습니다.
# [큰 흐름 1: 사전 동결된 설정(selection.json)과 데이터 불러오기]
# - 탐색 단계(CV)에서 확정된 모델 설정과 데이터 분할 ID를 그대로 로드합니다.
# - train, valid를 합쳐 '개발 데이터(16건)'를 만들고, 봉인되어 있던 'test(4건)'를 분리합니다.
plan = json.loads((HERE / "selection.json").read_text(encoding="utf-8"))
raw = pd.read_csv(HERE / "requests.csv").set_index("request_id")
develop = raw.loc[plan["train_ids"] + plan["valid_ids"]].copy()
test = raw.loc[plan["test_ids"]].copy()

# 제공: 행별 공식은 새 요청에도 동일하게 적용합니다. test로 통계나 설정을 학습하지 않습니다.
# [큰 흐름 2: 누수 없는 행별 특성 공학(Feature Engineering) 적용]
# - 통계치를 학습하는 것이 아니라 각 행별로 독립적으로 계산되는 log 변환이므로 개발 및 test 동일 적용
for table in (develop, test):
    table["log_input_chars"] = np.log1p(table["input_chars"])

# 동결된 하이퍼파라미터(max_depth, random_state 등)를 반영해 모델 객체 초기화
model = DecisionTreeClassifier(max_depth=plan["max_depth"], random_state=plan["random_state"])

# TODO B07a: 개발 자료 16건의 선택된 입력과 failed로 학습하세요. test는 넣지 않습니다.
features = plan["features"].copy() if isinstance(plan["features"], list) else list(plan["features"])
if plan.get("derived") and "log_input_chars" not in features:
    features.append("log_input_chars")
model.fit(develop[features], develop["failed"])
# TODO 끝

# 0·1 두 클래스가 있는 정상 자료입니다. classes_에서 양성 1의 위치를 확인합니다.
positive_column = model.classes_.tolist().index(1)

# [큰 흐름 4: 봉인된 Test 데이터 추론 및 확률 계산]
# - 학습에 일체 참여하지 않은 test 데이터를 입력해 실패(1) 확률 추정값 추출
# TODO B07b: test의 실패 확률을 구하세요. predict_proba의 positive_column 열만 선택합니다.
probability = model.predict_proba(test[features])[:, positive_column]
# TODO 끝

# 동결된 임계값 (threshold)을 기준으로 0 또는 1의 최종 클래스 예측값 산출
prediction = (probability > plan["threshold"]).astype(int)

# [큰 흐름 5: 최종 평가지표 산출 (F1 및 ROC-AUC)]
# - F1 점수에는 0/1 최종 클래스 예측값을, ROC-AUC에는 순위 평가를 위한 연속 확률 점수를 전달
# TODO B07c: F1에는 0/1 예측값, AUC에는 실패 확률을 넣으세요.
f1 = f1_score(test["failed"], prediction, zero_division=0)
auc = roc_auc_score(test["failed"], probability)
# TODO 끝

metrics = {"n": len(test), "Accuracy": accuracy_score(test["failed"], prediction),
           "Precision": precision_score(test["failed"], prediction, zero_division=0),
           "Recall": recall_score(test["failed"], prediction, zero_division=0),
           "F1": f1, "ROC_AUC": auc, "TP": int(((test["failed"] == 1) & (prediction == 1)).sum()),
           "actual_failed": int(test["failed"].sum()), "threshold": plan["threshold"]}
result = pd.DataFrame({"request_id": test.index, "actual": test["failed"].to_numpy(),
                       "probability_failed": probability, "predicted": prediction})
result.to_csv(HERE / "test_predictions.csv", index=False, encoding="utf-8-sig")
(HERE / "test_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
print("개발/최종평가:", len(develop), len(test))
print(result.round(3).to_string(index=False))
print("혼동행렬:", confusion_matrix(test["failed"], prediction, labels=[0, 1]).tolist())
print(f"Accuracy={metrics['Accuracy']:.3f}, Precision={metrics['Precision']:.3f}, Recall={metrics['Recall']:.3f}, F1={f1:.3f}, AUC={auc:.3f}")
print("저장: test_predictions.csv, test_metrics.json")
print("08번은 이 설정 그대로 재실행합니다. test를 보고 06번 설정을 다시 고르지 않습니다.")

"""
=============================================================================
[Final Evaluation Executive Summary Report]
- 프로젝트 요약 : 동결된 설정 기반 최종 모델 배포 및 검증 세트 독립 평가
- 데이터 계약   : Train/Valid(16건) 개발 통합 학습 완료 후 Test(4건) 단 1회 추론
- 주요 성과     : 데이터 누수 원천 차단 및 사전 정의된 임계값(0.5)을 통한 객관적 지표 산출
- 고찰 및 한계  : 소표본 테스트 환경으로 인한 통계적 변동성 존재하며, 실서비스 
                  배포 전 추가 샘플 확보 및 임계값 튜닝 프로세스 수립 필요
=============================================================================
"""