"""실습 02 응용: 가상 확률로 임계값만 바꿉니다. 최종 모델의 임계값을 탐색하는 코드가 아닙니다."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, roc_auc_score

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# 실제 정답(y): 성공(0) 2건, 실패(1) 2건
y = np.array([0, 0, 1, 1]) # 총 4건

# 모델이 출력한 '실패(1)일 연속 추정 확률' (predict_proba의 실패 열 값에 해당)
score = np.array([0.10, 0.40, 0.35, 0.80])

rows = []

# 기본 임계값(0.5)과 기준을 완화한(0.3) 두 가지 상황을 시뮬레이션함.
for threshold in [0.5, 0.3]:

    # [핵심 학습 1] 연속 확률(score)을 임계값(threshold) 기준으로 0과 1의 클래스로 변환하기
    # 1) (score > threshold): "같은 값은 성공(0)"이라는 조건이므로 이상(>=)이 아니라 초과(>)
    #    비교 결과는 [False, False, True, True] 같은 불리언 (True/False) 배열로 나옵니다.
    # 2) .astype(int): 파이썬/넘파이에서 True는 정수 1, False는 정수 0으로 변환되는 성질을 이용.
    #   - threshold = 0.5일 때: 0.80만 0.5보다 크므로 [0, 0, 0, 1] (실제 실패 2건 중 0.35를 놓쳐 FN=1 발생)
    #   - threshold = 0.3일 때: 0.4, 0.35, 0.80이 모두 크므로 [0, 1, 1, 1] (실패 2건 다 찾았으나 0.40에서 오탐 FP=1 발생)

    # TODO A02: 확률이 threshold보다 클 때만 실패1로 바꾸세요. 같은 값은 성공0입니다.
    # prediction = np.zeros(len(y), dtype=int)
    prediction = (score > threshold).astype(int)
    # TODO 끝
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()

    # [핵심 학습 2] 업무상의 가정 오류 비용(assumed_cost)과 roc_auc_score의 특징 비교
    # - assumed_cost (fp + 5*fn): "헛경고(FP)는 확인 비용이 1이지만, 실제 실패를 놓치는 것(FN)은 피해가 5배(5) 크다"는 가정입니다.
    #   threshold를 0.5 -> 0.3으로 낮추면 FP는 0->1로 늘지만 치명적인 FN이 1->0으로 줄어 총비용이 5 -> 1로 감소하고 F1도(0.667 -> 0.800) 오릅니다.
    # - roc_auc_score(y, score): ★주의★ 첫 번째 인자는 정답(y)이지만, 두 번째 인자는 0/1로 바뀐 'prediction'이 아니라 원본 확률 'score'를 넣습니다!
    #   AUC는 임계값과 무관하게 원본 확률 점수들의 '줄 세우기(순위)' 능력만 보므로, threshold가 0.5든 0.3이든 항상 0.75로 동일하게 유지됩니다.
    rows.append({"threshold": threshold, "FP": fp, "FN": fn, "F1": f1_score(y, prediction),
                 "assumed_cost": fp + 5*fn, "AUC": roc_auc_score(y, score)})
result = pd.DataFrame(rows)
print(result.round(3).to_string(index=False))
result.to_csv(OUT / "threshold_comparison.csv", index=False, encoding="utf-8-sig")

# [오늘의 메인 교훈]
# 임계값을 조정하면 같은 모델(같은 AUC)에서도 FP·FN 개수와 운영 비용이 크게 달라집니다.
# 단, 최종 test 데이터를 열어본 뒤에 비용이나 F1을 높이려고 임계값을 바꾸면 데이터 누수(반칙)가 되므로, 본 프로젝트의 최종 평가 임계값은 사전에 0.5로 고정합니다.
print("cost는 FP 비용1, FN 비용5라는 가정입니다. 최종 평가 임계값은 사전에 0.5로 고정합니다.")
