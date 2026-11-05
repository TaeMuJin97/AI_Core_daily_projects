"""
==============================================================================
[실습 보고서: 03_finetune.py - Head-only vs Partial Fine-tuning 학습 범위별 성능 비교]
1. 실험 목적: 동일한 사전학습 가중치(source_backbone.npz)와 초기 조건에서 분류기만 학습하는
              Head-only 전략과 상위 합성곱 층(model[4])까지 함께 미세조정하는 Partial 전략의
              학습 가능 파라미터 수(trainable) 및 검증 정확도(valid_accuracy)를 비교함.
2. 고정 조건: 난수 시드(seed=14), 입력 규격(32x32 RGB), BatchNorm 통계 고정(model.eval()),
              Optimizer(AdamW, lr=0.003), 학습 횟수(8 Epochs)
3. 변경 조건: 
   - head: model[9] (nn.Linear(256, 3))만 requires_grad=True (771개 파라미터)
   - partial: model[9] + model[4] (nn.Conv2d(8, 16, 3, bias=False)) requires_grad=True (1,923개 파라미터)
4. 주요 산출물: 
   - 콘솔 출력: 전략별 학습 가능 파라미터 수(trainable) 및 검증 정확도(valid_accuracy) 비교표
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
train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)

# [핵심 포인트 1: 소규모 데이터셋의 인메모리(In-memory) 텐서 스택]
# 개별 이미지 텐서 [3, 32, 32]를 torch.stack으로 묶어 [N, 3, 32, 32] 형태의 전체 배치 텐서로 한 번에 구성합니다.
X_train = torch.stack([train[i][0] for i in range(len(train))])
y_train = torch.tensor(train.targets, dtype=torch.long)
X_valid = torch.stack([valid[i][0] for i in range(len(valid))])
y_valid = torch.tensor(valid.targets, dtype=torch.long)

results = []
for strategy in ["head", "partial"]:
    # [핵심 포인트 2: 공정한 비교를 위한 루프 내부 시드 재고정]
    # 두 전략이 정확히 동일한 무작위 Head 초기값에서 출발하도록 매 전략 시작 시 시드를 14로 초기화합니다.
    torch.manual_seed(14)  # 두 전략은 같은 source·Head 초기값·분할·8회 학습
    
    # 제공 부분: 0~8은 Backbone, 9는 새 3클래스 Head입니다.
    # 인덱스 구조: [0]Conv1, [1]BN1, [2]ReLU, [3]MaxPool, [4]Conv2, [5]BN2, [6]ReLU, [7]AdaptiveAvgPool, [8]Flatten, [9]Linear
    model = nn.Sequential(
        nn.Conv2d(3, 8, 3, padding=1, bias=False), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(8, 16, 3, padding=1, bias=False), nn.BatchNorm2d(16), nn.ReLU(),
        nn.AdaptiveAvgPool2d((4, 4)), nn.Flatten(), nn.Linear(256, 3),
    )
    # 안전한 수치 배열만 읽습니다. Target 이미지로 사전학습한 파일이 아닙니다.
    with np.load(DATA / "source_backbone.npz", allow_pickle=False) as saved:
        state = model.state_dict()
        state.update({name: torch.from_numpy(saved[name].copy()) for name in saved.files})
    model.load_state_dict(state)

    # 먼저 전체 파라미터를 동결(Freeze)합니다.
    for p in model.parameters():
        p.requires_grad = False
        
    # TODO B03: 두 전략에서 Head(9)를 열고, partial일 때 두 번째 Conv(4)도 여세요.
    # BEGIN B03
    # [핵심 포인트 3: 전략별 학습 범위(Unfreeze) 단계적 개방]
    # 1) 공통: 새 분류층인 model[9] (Linear: 256*3 + 3 = 771개)는 항상 학습 가능하게 엽니다.
    for p in model[9].parameters():
        p.requires_grad = True
    # 2) Partial Fine-tuning: 상위 특징 추출 층인 model[4] (Conv2d: 입력8 * 출력16 * 3 * 3 = 1,152개)를 추가로 엽니다.
    if strategy == "partial":
        for p in model[4].parameters():
            p.requires_grad = True
    # END B03
    
    # [핵심 포인트 4: BatchNorm 통계 고정 정책]
    # requires_grad 여부와 무관하게 BatchNorm2d가 train() 상태면 running_mean/var가 변경됩니다.
    # 사전학습된 정규화 통계가 흔들리지 않도록 두 전략 모두 model.eval() 상태에서 가중치만 업데이트합니다.
    model.eval()  # BN 통계는 두 전략 모두 고정합니다.
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.0)
    
    for epoch in range(8):
        optimizer.zero_grad()
        loss = nn.CrossEntropyLoss()(model(X_train), y_train)
        loss.backward()
        optimizer.step()
        
    with torch.no_grad():
        pred = model(X_valid).argmax(1)
        
    results.append([
        strategy,
        sum(p.numel() for p in model.parameters() if p.requires_grad),
        accuracy_score(y_valid, pred),
    ])

print(pd.DataFrame(results, columns=["strategy", "trainable", "valid_accuracy"]).round(4).to_string(index=False))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 전략별 학습 가능 파라미터 수(trainable) 계산 검증:
   - head 전략: model[9] (Linear(256, 3))만 열려 256 * 3 + 3 = 771개가 학습됨.
   - partial 전략: model[9](771개)에 더해 두 번째 합성곱 층인 model[4] (Conv2d(8, 16, 3, bias=False))의
     8 * 16 * 3 * 3 = 1,152개가 추가 개방되어 총 771 + 1,152 = 1,923개가 학습됨.
2. 학습 범위 확장에 따른 성능 변화:
   - Source와 Target 데이터 간에 미세한 도메인 차이가 존재할 때, Head만 학습하는 것보다
     상위 합성곱 층(model[4])의 필터 가중치까지 함께 조정하는 Partial Fine-tuning이 Target 도메인의
     형태적 특징에 더 잘 적응하여 검증 정확도(valid_accuracy)가 개선되는지 비교 확인할 수 있음.
==============================================================================
"""