"""
==============================================================================
[실습 보고서: 02_iou.py - IoU 수동 계산 및 1:1 그리디 매칭을 통한 TP/FP/FN·Precision·Recall 산출]
1. 실험 목적: 신뢰도(Confidence) 내림차순으로 정렬된 예측 박스 4개와 정답 박스 3개의 IoU를 계산하고,
              클래스 일치 여부 및 평가 IoU 임계값(>=0.5) 기준의 1:1 매칭 규칙을 적용해
              TP(정탐), FP(오탐/중복탐지), FN(미탐) 및 Precision·Recall을 정량적으로 도출함.
2. 핵심 개념 및 알고리즘:
   - 교집합(Intersection) 영역: 겹치는 사각형의 왼쪽 위는 max(x1), max(y1)이고 오른쪽 아래는 min(x2), min(y2)임.
     박스가 서로 떨어져 있으면 끝점-시작점이 음수가 되므로 max(0, ...) 처리로 너비/높이를 0으로 만듦.
   - 합집합(Union) 영역: (예측 박스 면적) + (정답 박스 면적) - (교집합 면적). 포함-배제 원리로 중복 면적을 한 번 뺌.
   - 1:1 매칭과 used 집합: 신뢰도가 높은 예측부터 우선권을 가지며, 이미 매칭된 정답 객체(j in used)에
     뒤늦게 또 매칭되는 중복 예측 박스는 IoU가 0.5를 넘더라도 가차 없이 FP(거짓 양성)로 처리됨.
3. 주요 산출물: p02_matching.csv (예측 박스별 최대 IoU 및 TP/FP 판정 결과표)
==============================================================================
"""
"""실습 02. 손으로 정한 예측 4개를 정답 3개와 비교합니다. YOLO 결과가 아닙니다."""
from pathlib import Path
import numpy as np
import pandas as pd

# 기존: BASE = Path(__file__).resolve().parent  (절대 경로라 '01_기본필수'가 포함됨)
BASE = Path(".")  # 현재 위치 기준 상대 경로 ('data/scene.png'로만 전달되어 한글이 안 섞임!)
# [핵심 개념 1: 평가 매칭 전 Confidence 내림차순 정렬의 중요성]
# 객체 탐지 평가에서는 항상 모델이 가장 확신하는(Confidence가 높은) 예측 박스부터 먼저 정답과 매칭할 기회를 줍니다.
pred = pd.read_csv(BASE / "data/boxes_fixture.csv")  # confidence 내림차순 예시
truth = pd.read_csv(BASE / "data/boxes_gt.csv")

# [핵심 개념 2: 정답 객체 중복 매칭 방지를 위한 집합(Set) 상태 관리]
# 정답 객체 1개에는 오직 1개의 예측 박스만 TP로 인정받을 수 있습니다. 이미 짝을 찾은 정답의 인덱스를 기록합니다.
used = set()  # 하나의 정답은 한 번만 TP로 연결합니다.
rows = []

for p in pred.itertuples():
    overlaps = []
    for g in truth.itertuples():
        # [핵심 개념 3: 두 Bounding Box 간의 교집합(Intersection)과 합집합(Union) 기하학]
        # 1) 겹치는 영역의 가로(width): 두 박스의 오른쪽 끝 중 더 왼쪽 값(min) - 왼쪽 끝 중 더 오른쪽 값(max)
        # 2) 겹치는 영역의 세로(height): 두 박스의 아래쪽 끝 중 더 위쪽 값(min) - 위쪽 끝 중 더 아래쪽 값(max)
        # 3) 두 박스가 아예 안 겹치면 뺄셈 결과가 음수가 나오므로 max(0, ...)로 방어합니다.
        width = max(0, min(p.x2, g.x2) - max(p.x1, g.x1))
        height = max(0, min(p.y2, g.y2) - max(p.y1, g.y1))
        intersection = width * height
        
        # 합집합 면적 = A 면적 + B 면적 - 겹친 면적(두 번 더해졌으므로 한 번 빼줌)
        union = (p.x2 - p.x1) * (p.y2 - p.y1) + (g.x2 - g.x1) * (g.y2 - g.y1) - intersection
        
        # >>> B02
        # 요구: intersection을 union으로 나누어 iou를 계산하세요.
        # 이 실습의 데이터는 모두 양의 면적이므로 union은 0이 아닙니다.
        # [핵심 구현: IoU(Intersection over Union) 비율 산출]
        # 0이면 전혀 안 겹침, 1이면 위치와 크기가 완벽히 일치함을 뜻합니다. (실무 방어 코드에서는 union + 1e-8 사용)
        iou = intersection / union
        # <<< B02
        overlaps.append(iou)
        
    matched = False
    # [핵심 개념 4: 가장 많이 겹치는 정답부터 탐색 (np.argsort 내림차순)]
    # overlaps 앞에 마이너스(-)를 붙여 정렬하면 IoU가 가장 큰 정답의 인덱스(j)부터 순서대로 꺼내옵니다.
    for j in np.argsort(-np.asarray(overlaps)):
        # 조건 1: 예측 클래스와 정답 클래스가 다르면 아무리 위치가 겹쳐도 매칭 불가 (Wrong Class 방지)
        # 조건 2: 이미 앞선(더 높은 점수의) 예측 박스와 매칭되어 주인이 있는 정답(j in used)이면 건너뜀 (Duplicate Box 방지)
        if truth.iloc[j].class_id != p.class_id or j in used:
            continue
        # >>> B03
        # 요구: 같은 클래스의 미사용 정답에 IoU>=0.5이면 연결하고 used에 기록하세요.
        # [핵심 구현: 평가 IoU 임계값(0.5) 돌파 여부 확인 및 1:1 매칭 확정]
        # mAP50의 기준인 IoU >= 0.5를 만족하면 정탐(TP)으로 확정하고, 해당 정답 j를 used에 넣어 잠근 뒤 루프를 탈출(break)합니다.
        if overlaps[j] >= 0.5:
            matched = True
            used.add(j)
            break
        # <<< B03
        
    rows.append([p.class_id, p.confidence, round(max(overlaps), 4), "TP" if matched else "FP"])

table = pd.DataFrame(rows, columns=["class", "confidence", "max_iou", "result"])
print(table.to_string(index=False))

# [핵심 개념 5: Detection의 TP, FP, FN 건수 및 Precision·Recall 산식]
# - TP: 매칭에 성공한 정답(=매칭에 성공한 예측)의 수 -> len(used)
# - FP: 전체 예측 수(len(pred)) 중 TP가 되지 못한 나머지 모든 예측 (배경 오탐, 클래스 오분류, 중복 탐지 포함)
# - FN: 전체 정답 수(len(truth)) 중 끝까지 어떤 예측과도 연결되지 못한 미탐지 정답 객체 수
tp = len(used)
fp = len(pred) - tp
fn = len(truth) - tp
print("TP/FP/FN:", tp, fp, fn)

# - Precision(정밀도) = TP / (TP + FP) = TP / len(pred) -> 모델이 뱉은 박스 중 진짜 정답의 비율
# - Recall(재현율) = TP / (TP + FN) = TP / len(truth) -> 실제 존재하는 정답 중 모델이 찾아낸 비율
print("Precision/Recall:", round(tp / len(pred), 4), round(tp / len(truth), 4))
table.to_csv(BASE / "p02_matching.csv", index=False, encoding="utf-8-sig")