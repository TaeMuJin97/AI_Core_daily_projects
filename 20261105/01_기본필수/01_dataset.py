"""Day14: 제공된 정상 이미지로 학습합니다. test는 읽지 않습니다.

==============================================================================
[실습 보고서: 01_dataset.py - ImageFolder 기반 데이터셋 구조 검증 및 클래스 불균형 진단]
1. 실험 목적: torchvision.datasets.ImageFolder를 사용하여 train, valid, test 분할의 폴더 구조를 읽고,
              모든 분할이 동일한 라벨 계약(class_to_idx)을 따르는지 검증하며 클래스별 샘플 분포를 확인함.
2. 고정 조건: 난수 시드(seed=14), 데이터 경로(data/train, data/valid, data/test), 클래스 수(3개)
3. 핵심 구현: 
   - ImageFolder(DATA / "train")을 통해 하위 폴더 알파벳 정렬 기반의 class_to_idx 매핑 확인
   - train, valid, test 각 분할의 클래스별 샘플 수(counts) 집계 및 라벨 매핑 일치 여부(bool) 검증
   - 데이터 누수 방지를 위해 test 분할은 매핑 및 개수 감사(Audit)만 수행하고 모델 학습/선택에는 미사용
4. 주요 산출물: 
   - 콘솔 출력: class_to_idx 딕셔너리, 분할별 클래스 개수 리스트([circle, square, triangle]), 매핑 일치 여부(True)
==============================================================================
"""
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

# TODO B01: ImageFolder로 train 폴더를 읽으세요. root는 필수 경로입니다.
# BEGIN B01
# [핵심 포인트 1: ImageFolder의 라벨 계약(class_to_idx)]
# ImageFolder는 root 하위 폴더 이름을 알파벳순으로 정렬하여 정수 라벨(0, 1, 2)을 자동 부여합니다.
train = ImageFolder(DATA / "train")  # train 폴더로 바꾸세요.
# END B01
print("class_to_idx:", train.class_to_idx)

# [핵심 포인트 2: 분할 간 라벨 일관성 및 클래스 불균형(Imbalance) 사전 점검]
# train은 다수/소수 클래스 불균형(예: [120, 40, 20])이 존재하는지 확인하고,
# valid와 test가 동일한 클래스 순서(class_to_idx)와 평가용 분포를 유지하는지 점검합니다.
for split in ["train", "valid", "test"]:
    dataset = ImageFolder(DATA / split)
    counts = [dataset.targets.count(i) for i in range(3)]
    print(split, "개수:", counts, "같은 매핑:", dataset.class_to_idx == train.class_to_idx)
# test는 파일명·라벨 매핑만 확인했습니다. 모델 예측에는 사용하지 않습니다.

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 라벨 계약(class_to_idx) 일관성 확인:
   - 알파벳 순서에 따라 {'circle': 0, 'square': 1, 'triangle': 2}로 매핑되었으며,
     train, valid, test 세 분할 모두 '같은 매핑: True'로 라벨 뒤바뀜 위험이 없음을 확인함.
2. 클래스 불균형(Class Imbalance) 진단:
   - train 분할에서 클래스별 샘플 수가 불균형하게 분포되어 있으므로, 단순 Accuracy만 볼 경우
     다수 클래스(circle) 편향을 놓칠 수 있어 이후 실습에서 Macro F1 및 Recall 추적이 필수적임.
==============================================================================
"""