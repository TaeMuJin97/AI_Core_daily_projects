"""
==============================================================================
[실습 보고서: 03_finetune_2.py - Head-only와 Partial Fine-tuning 전략별 성능 및 학습 이력 비교 자동화]
1. 실험 목적: Head-only와 Partial 두 가지 전이학습 전략을 동일한 데이터 및 8 Epoch 예산에서 학습시키고,
              검증 손실(Valid Loss) 기준 Best Epoch 가중치를 복원하여 정확도(Accuracy), Macro F1,
              소수 클래스(triangle) Recall, 그리고 소요 시간(seconds)을 CSV 보고서로 자동 내보냄.
2. 고정 조건: 시드(seed=14), Optimizer(AdamW, lr=0.003, weight_decay=0.0001), 총 8 Epochs, BatchNorm 고정(model.eval())
3. 변경 조건: 
   - head: 분류 Head만 학습 (파라미터 771개)
   - partial: model[4] (Conv2조) + model[9] (Head) 동시 학습 (파라미터 1,923개)
4. 주요 산출물: 
   - outputs/finetune_comparison.csv (전략별 파라미터 수, 최적 에폭, Accuracy, Macro F1, triangle Recall 기록표)
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

# TODO A03: Head-only, Partial 두 전략만 비교하세요. 데이터와 epoch는 고정합니다.
# BEGIN A03
# [핵심 포인트 1: 비교 실험 군(Experiments) 설정]
# 지시사항에 따라 학습 범위 전략인 "head"와 "partial"을 순서대로 비교하도록 튜플 리스트를 구성합니다.
experiments = [("head", "none"), ("partial", "none")]  # partial 후보를 추가하세요.
# END A03

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
            
    # BatchNorm 통계 고정 및 현재 학습 가능한 파라미터만 Optimizer에 전달
    model.eval()
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=0.003, weight_decay=0.0001)
    
    counts = torch.bincount(y_train, minlength=3).float()
    inverse = 1.0 / counts
    class_weights = inverse / inverse.mean()
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
        
        # [핵심 포인트 2: Best Model Checkpointing (Validation Loss 기준 최적 가중치 백업)]
        # 학습 도중 valid_loss가 가장 낮아졌을 때의 모델 상태(state_dict)를 deepcopy 방식으로 안전하게 보관합니다.
        if vl < best_loss:
            best_loss=vl;best_epoch=epoch
            best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            
    elapsed = time.perf_counter()-started
    
    # 가장 성능이 좋았던 에폭의 가중치를 모델에 복원한 뒤 최종 평가를 수행합니다.
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

table=pd.DataFrame(rows);table.to_csv(OUT/"finetune_comparison.csv",index=False)
print(table.drop(columns="seconds").round(4).to_string(index=False))
print("시간은 finetune_comparison.csv에 기록: 기기별로 달라짐")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 자동 체크포인팅(Best Checkpoint)의 효과:
   - 단순 마지막 에폭(Epoch 8) 가중치를 쓰는 대신, 8번의 학습 중 Validation Loss가 최소였던
     best_epoch의 가중치를 복원하여 평가하므로 오버피팅에 의한 성능 저하를 방지함.
2. 다각도 평가지표 산출 (Accuracy vs Macro F1 vs 소수 클래스 Recall):
   - 전체 Accuracy 외에도 불균형 진단에 필수적인 Macro F1과 소수 클래스(triangle, 인덱스 2)의
     Recall(`triangle_recall`)을 함께 기록하여 전략별 실질 성능을 명확히 비교함.
==============================================================================
"""