"""
==============================================================================
[실습 보고서: 04_imbalance.py - 클래스 불균형 상황에서 Accuracy와 Macro F1 지표의 착시 현상 진단]
1. 실험 목적: 소수 클래스가 포함된 불균형 정답 레이블(y_true)에 대해 모델이 전부 다수 클래스로만 예측(y_pred)했을 때,
              Accuracy는 높아 보이지만 Macro F1과 클래스별 Recall이 0으로 무너지는 현상을 직접 확인함.
2. 고정 조건: 가상의 정답 분포(y_true: circle 12개, square 6개, triangle 3개 / 총 21개), 올인 예측(y_pred: 전부 0번 circle)
3. 핵심 구현: 
   - sklearn.metrics.accuracy_score를 통한 전체 정확도 산출
   - sklearn.metrics.f1_score에 average="macro", labels=[0,1,2], zero_division=0을 적용해 클래스별 동등 비중 F1 산출
   - classification_report를 통한 클래스별 Precision, Recall, Support 상세 리포트 출력
4. 주요 산출물: 
   - 콘솔 출력: 클래스별 개수, Accuracy, Macro F1, 상세 분류 보고서
==============================================================================
"""

"""Day14: 제공된 정상 이미지로 학습합니다. test는 읽지 않습니다."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
from torch import nn
from torchvision.datasets import ImageFolder
from torchvision import transforms as tr
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

torch.set_num_threads(1)
torch.manual_seed(14)
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE

# 여기서는 [0,1] RGB 32×32로 학습한 교육용 source 가중치를 사용합니다.
# ImageNet ResNet18과 입력 변환을 섞지 않습니다.
transform = tr.Compose([tr.Resize((32, 32)), tr.ToTensor()])

# 손으로 읽는 지표 예제입니다. 모델의 실제 예측이라고 주장하지 않습니다.
# [핵심 포인트 1: 불균형 데이터셋 구성]
# circle(0번) 12개, square(1번) 6개, triangle(2번) 3개로 구성된 불균형 정답 배열입니다.
y_true = [0] * 12 + [1] * 6 + [2] * 3
# 모델이 모든 샘플을 무조건 다수 클래스인 0번(circle)으로만 예측한 상황을 가정합니다.
y_pred = [0] * 21

print("클래스 수:", [y_true.count(i) for i in range(3)])
print("Accuracy:", round(accuracy_score(y_true, y_pred), 4))

# TODO B04: f1_score에 average="macro", labels=[0,1,2], zero_division=0을 넣으세요.
# BEGIN B04
# [핵심 포인트 2: Macro F1을 통한 소수 클래스 실패 포착]
# Accuracy만 보면 12/21 = 57.1%로 그럴싸해 보이지만, Macro F1을 구하면 소수 클래스를 전혀 맞히지 못한 참상을 정확히 반영할 수 있습니다.
macro = f1_score(y_true, y_pred, labels=[0, 1, 2], average="macro", zero_division=0)  # f1_score 계산으로 바꾸세요.
# END B04

print("Macro F1:", round(macro, 4))
print(classification_report(y_true, y_pred, labels=[0, 1, 2], target_names=["circle", "square", "triangle"], zero_division=0, digits=3))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Accuracy의 함정 진단:
   - 다수 클래스(circle)만 전부 맞히고 소수 클래스(square, triangle)를 전부 놓쳤음에도 불구하고,
     Accuracy는 약 0.5714로 57% 이상의 높은 점수가 나옴.
     
2. Macro F1의 타당성 입증:
   - 각 클래스의 F1 점수를 단순 평균(Macro) 내면 소수 클래스의 F1이 0이므로 전체 Macro F1 역시 대폭 낮아져,
     불균형 데이터에서 모델의 실질적인 균형 성능을 평가하는 주 지표로서의 가치를 증명함.
==============================================================================
"""