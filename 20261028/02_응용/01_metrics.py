"""실습 01 응용: 모델 예시와 전부 성공으로 예측하는 기준선을 비교합니다."""
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# 실제 정답: 20건 중 성공(0)이 14건, 실패(1)가 6건인 불균형 데이터 상황입니다.
y = [0]*14 + [1]*6

# 두 가지 가짜 모델의 예측값
# - example: 일부는 맞고 일부는 틀린 현실적인 예측치
# - all_success: 아무런 판단 없이 20건 모두 "성공(0)"으로 찍어버리는 깡통 모델
predictions = {"example": [0]*10 + [1]*4 + [0]*4 + [1]*2, "all_success": [0]*20}

rows = []
for name, pred in predictions.items():
    # [핵심 학습 1] confusion_matric와 .ravel()의 조합
    # labels=[0, 1]을 줘서 행렬의 위치가 뒤섞이지 않게 (음성, 양성) 순서를 고정합니다.
    # .ravel()은 2x2 모양의 2차원 표를 1차원 리스트로 쭉 펴줍니다.
    # 덕분에 [TN, FP, FN, TP] 순서대로 변수 4개에 깔끔하게 나누어 담을 수 있습니다.
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    # TODO A01: 현재 후보의 F1을 계산하세요. 분모 0은 0으로 표시합니다.

    # [핵심 학습 2] zero_division=0 이 필요한 이유
    # 'all_success' 모델은 실패(1)라고 예측한 적이 한 번도 없습니다.
    # 정밀도 (Precision)와 F1을 계산할 때 "예측한 실패 수"가 분모로 들어가는데, 이 분모가 0이 되어버립니다.
    # 프로그램이 에러를 뿜으며 멈추는 것을 막기 위해 "분모가 0이면 그냥 점수를 0점으로 처리해라"라고 안전장치를 거는 것.
    f1 = f1_score(y, pred, zero_division=0)
    # TODO 끝
    rows.append({"model": name, "Accuracy": accuracy_score(y, pred),
                 "Precision": precision_score(y, pred, zero_division=0),
                 "Recall": recall_score(y, pred, zero_division=0), "F1": f1,
                 "FP": fp, "FN": fn, "TP": tp})
    
print(pd.DataFrame(rows).round(3).to_string(index=False))

# [오늘의 메인 교훈]
# all_success 모델은 20문제 중 14문제를 맞혀서 정확도(Accuracy)가 무려 70%입니다.
# 하지만 정작 우리가 잡아야 할 진짜 목표인 '실패(1)'는 1건도 찾지 못했습니다 (Recall = 0).
# 불균형 데이터에서 정확도(Accuracy)만 보고 모델이 좋다고 속으면 안 되는 이유입니다.
print("정확도가 높은 all_success도 실패 6건을 하나도 찾지 못합니다.")
