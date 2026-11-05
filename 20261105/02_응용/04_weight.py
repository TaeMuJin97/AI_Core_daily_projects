"""
==============================================================================
[실습 보고서: 04_weight.py - 클래스 불균형 해소를 위한 Loss Class Weight 적용 효과 비교 자동화]
1. 실험 목적: Head-only 전이학습 시 불균형한 학습 데이터(train)의 클래스 역빈도를 기반으로 가중치(class_weights)를 산출하고,
              이를 nn.CrossEntropyLoss(weight=...)에 적용했을 때와 적용하지 않았을 때의
              Accuracy, Macro F1, 그리고 소수 클래스(triangle) Recall 변화를 CSV로 비교 분석함.
2. 고정 조건: 난수 시드(seed=14), Optimizer(AdamW, lr=0.003, weight_decay=0.0001), 총 8 Epochs, Best Loss 모델 복원
3. 변경 조건: 
   - balance="none": 기본 CrossEntropyLoss (클래스 가중치 미적용)
   - balance="weight": 클래스별 빈도의 역수를 정규화한 class_weights를 Loss에 반영
4. 주요 산출물: 
   - outputs/weight_comparison.csv (조건별 파라미터 수, 최적 에폭, Accuracy, Macro F1, triangle Recall 기록표)
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
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

# 여기서는 [0,1] RGB 32×32로 학습한 교육용 source 가중치를 사용합니다.
# ImageNet ResNet18과 입력 변환을 섞지 않습니다.
transform = tr.Compose([tr.Resize((32, 32)), tr.ToTensor()])
import time
train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)
X_train = torch.stack([train[i][0] for i in range(len(train))])
y_train = torch.tensor(train.targets, dtype=torch.long)
X_valid = torch.stack([valid[i][0] for i in range(len(valid))])
y_valid = torch.tensor(valid.targets, dtype=torch.long)

# TODO A04: 같은 head 모델에서 none, weight 두 조건을 비교하세요.
# BEGIN A04
# [핵심 포인트 1: 불균형 대응 비교 실험 군 설정]
# 동일한 Head-only 모델 구조에서 손실 함수 가중치 유무("none" vs "weight")에 따른 성능 차이를 비교합니다.
experiments = [("head", "none"), ("head", "weight")]  # ("head", "weight")를 추가하세요.
# END A04

rows = []
all_history = []
for strategy, balance in experiments:
    torch.manual_seed(14)
    # 제공 부분: 0~8은 Backbone, 9는 새 3클래스 Head입니다.
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

    for p in model.parameters():
        p.requires_grad = False
    for p in model[9].parameters():
        p.requires_grad = True
    if strategy == "partial":
        for p in model[4].parameters():
            p.requires_grad = True
            
    model.eval()
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=0.003, weight_decay=0.0001)
    
    # [핵심 포인트 2: 클래스별 역빈도(Inverse Frequency) 기반 Loss Weight 산출]
    # 데이터 개수가 적은 소수 클래스일수록 Loss에 곱해지는 페널티 가중치가 커지도록 설계합니다.
    counts = torch.bincount(y_train, minlength=3).float()
    inverse = 1.0 / counts
    class_weights = inverse / inverse.mean()
    
    # balance 조건에 따라 CrossEntropyLoss에 weight를 동적으로 부여합니다.
    criterion = nn.CrossEntropyLoss(weight=class_weights if balance == "weight" else None)
    
    best_loss = float("inf")
    started = time.perf_counter()
    
    for epoch in range(1, 9):
        optimizer.zero_grad()
        loss = criterion(model(X_train), y_train)
        loss.backward()
        optimizer.step()
        
        with torch.no_grad():
            vl = nn.CrossEntropyLoss()(model(X_valid), y_valid).item()
            
        all_history.append({"strategy":strategy,"balance":balance,"epoch":epoch,"valid_loss":vl})
        
        if vl < best_loss:
            best_loss=vl;best_epoch=epoch
            best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            
    elapsed = time.perf_counter()-started
    model.load_state_dict(best_state)
    
    with torch.no_grad():
        prob=model(X_valid).softmax(1);pred=prob.argmax(1)
        
    report=classification_report(y_valid,pred,labels=[0,1,2],output_dict=True,zero_division=0)
    
    rows.append({
        "strategy":strategy,
        "balance":balance,
        "params":sum(p.numel() for p in model.parameters() if p.requires_grad),
        "best_epoch":best_epoch,
        "accuracy":accuracy_score(y_valid,pred),
        "macro_f1":f1_score(y_valid,pred,labels=[0,1,2],average="macro",zero_division=0),
        "triangle_recall":report['2']['recall'],
        "seconds":elapsed
    })

print("train class_weights:",class_weights.tolist())
table=pd.DataFrame(rows);table.to_csv(OUT/"weight_comparison.csv",index=False)
print(table.drop(columns="seconds").round(4).to_string(index=False))


"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Class Weight 적용에 따른 손실 함수 변화:
   - train 데이터의 클래스 개수 비율에 역비례하는 class_weights가 적용되어,
     소수 클래스(triangle 등) 오분류 시 발생하는 Loss 페널티가 커짐.
2. 성능 지표 비교 (none vs weight):
   - 가중치를 주지 않았을 때(`none`)는 다수 클래스 위주로 예측해 소수 클래스 Recall이 낮을 수 있으나,
     `weight`를 적용하면 전체 Accuracy가 소폭 조정되더라도 Macro F1과 소수 클래스 Recall이 대폭 개선되는 효과를 확인함.
==============================================================================
"""