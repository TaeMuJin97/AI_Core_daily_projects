"""
==============================================================================================================
[실습 보고서: 06_transfer.py - ResNet18 전이학습(Transfer Learning) 전략 비교: Head-only vs Partial Fine-tuning]
1. 실험 목적: ImageNet 사전학습 가중치(ResNet18_Weights.IMAGENET1K_V1)를 불러온 뒤,
              분류기만 학습하는 'head' 모드와 상위 특징 추출 블록(layer4)까지 함께 미세조정하는 'partial' 모드의
              학습 가능 파라미터 수(trainable_params) 및 학습 경로 동작을 비교함.
2. 고정 조건: 사전학습 모델(resnet18), 입력 전처리(weights.transforms(), 224x224), Batch Size(4), Epoch(1),
              BatchNorm running 통계 고정(eval 모드 유지)
3. 변경 조건: 
   - head 모드: 백본 전체 동결(requires_grad=False), 교체된 model.fc(lr=0.001)만 학습
   - partial 모드: model.fc(lr=0.001) + model.layer4(requires_grad=True, lr=0.0001) 차등 학습률 적용
4. 주요 산출물: outputs/transfer_comparison.csv (모드별 학습 파라미터 수, 검증 손실/정확도, 소요 시간 비교표)
==============================================================================================================
"""

from pathlib import Path
import copy
import csv
import json
import time
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import pandas as pd

torch.manual_seed(42)
torch.set_num_threads(1)
root = Path(__file__).resolve().parent
out = root / "outputs"
out.mkdir(exist_ok=True)

from torchvision.models import resnet18, ResNet18_Weights

# 1. 사전학습 가중치 메타데이터 및 전용 전처리 파이프라인 로드
# ResNet18이 ImageNet 학습 당시 사용했던 해상도(224x224)와 정규화(mean, std) 규격을 그대로 가져옵니다.
weights = ResNet18_Weights.IMAGENET1K_V1
train = datasets.ImageFolder(root / "data" / "train", transform=weights.transforms())
valid = datasets.ImageFolder(root / "data" / "valid", transform=weights.transforms())

# 1 epoch는 학습 경로 점검용이다. 이 숫자로 일반화 성능의 우열을 단정하지 않는다.
rows = []
for mode in ["head", "partial"]:
    torch.manual_seed(42)
    # 가중치가 없으면 공식 다운로드. 무작위 초기화로 대체하지 않는다.
    model = resnet18(weights=weights)
    
    # [단계 1: 백본 전체 동결(Freeze)]
    # 모든 층의 가중치가 역전파 시 업데이트되지 않도록 미분 추적을 끕니다.
    for param in model.parameters():
        param.requires_grad = False
        
    # [단계 2: 분류기 헤드(Classifier Head) 교체]
    # 기존 1000개 클래스 분류용 fc 레이어를 현재 문제(horizontal/vertical 2진 분류)에 맞게 새로 생성합니다.
    # 새로 생성된 nn.Linear 레이어는 기본적으로 requires_grad=True 상태입니다.
    model.fc = nn.Linear(model.fc.in_features, 2)
    
    # 옵티마이저에 전달할 파라미터 그룹 설정 (새로 만든 fc 층은 비교적 큰 학습률 0.001 부여)
    groups = [{"params": model.fc.parameters(), "lr": 0.001}]
    
    if mode == "partial":
        # BEGIN A06
        # TODO A06: partial일 때만 layer4의 미분을 켠다.
        # [단계 3: 상위 블록(layer4) 동결 해제 및 차등 학습률(Differential Learning Rate) 적용]
        # 입력에 가까운 초기 층(layer1~3)은 범용 특징을 유지하도록 둔 채, 고수준 특징을 담당하는 layer4만 미분을 켭니다.
        for param in model.layer4.parameters():
            param.requires_grad = True
        # END A06
        # 사전학습된 layer4의 가중치가 급격히 망가지지 않도록 fc보다 1/10 작은 학습률(0.0001)을 부여합니다.
        groups.append({"params": model.layer4.parameters(), "lr": 0.0001})
        
    optimizer = torch.optim.AdamW(groups, weight_decay=0.0001)
    train_loader = DataLoader(train, batch_size=4, shuffle=True, num_workers=0,
                              generator=torch.Generator().manual_seed(42))
    
    # [핵심 포인트: 소규모 배치(Batch Size=4) 전이학습 시 BatchNorm2d 통계 고정]
    # 작은 배치로 학습할 때 BatchNorm이 현재 배치의 평균/분산으로 running 통계를 갱신하면 사전학습 분포가 무너집니다.
    # 따라서 모델 전체를 eval()로 두어 BN running 통계를 고정한 뒤, 학습할 모듈만 선택적으로 다루되 BN은 eval()을 유지합니다.
    model.eval()  # BN running 통계는 두 조건 모두 고정한다.
    model.fc.train()
    if mode == "partial":
        model.layer4.train()
        for layer in model.layer4.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()
                
    # 1 Epoch 학습 수행 및 소요 시간(초) 측정
    start = time.perf_counter()
    for images, labels in train_loader:
        optimizer.zero_grad()
        nn.functional.cross_entropy(model(images), labels).backward()
        optimizer.step()
    training_seconds = time.perf_counter() - start
    
    # 검증 데이터셋 평가
    model.eval()
    total_loss, correct, count = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in DataLoader(valid, batch_size=4):
            logits = model(images)
            total_loss += nn.functional.cross_entropy(logits, labels).item()*len(labels)
            correct += (logits.argmax(1)==labels).sum().item()
            count += len(labels)
            
    # p.requires_grad가 True인 파라미터 개수만 합산하여 실제 업데이트 대상 파라미터 규모를 기록합니다.
    rows.append(dict(mode=mode, pretrained=weights.name, image_size=224, epochs=1,
                     trainable_params=sum(p.numel() for p in model.parameters() if p.requires_grad),
                     valid_loss=total_loss/count, valid_accuracy=correct/count, training_seconds=training_seconds))

print(pd.DataFrame(rows).drop(columns="training_seconds").round(4).to_string(index=False))
pd.DataFrame(rows).to_csv(out / "transfer_comparison.csv", index=False)

"""
======================================================================================================================================================
[실험 결과 요약 및 진단 보고]
1. 학습 가능 파라미터 수(trainable_params) 비교:
   - head 모드: model.fc(입력 512 -> 출력 2)의 가중치(512*2 = 1,024)와 편향(2)만 활성화되어 총 1,026개만 학습됨.
   - partial 모드: model.fc(1,026개)에 더해 ResNet18의 마지막 스테이지인 layer4 전체 파라미터가 추가되어 약 839만 개가 학습됨.
2. 차등 학습률(Parameter Groups)의 역할:
   - 무작위로 초기화된 fc 층은 빠르게 수렴하도록 lr=0.001을 적용하고, 이미 잘 학습된 layer4는 기존 표현력을 보존하며 미세조정되도록 lr=0.0001로 낮춰 안정성을 확보함.
3. BatchNorm 고정 효과:
   - 작은 배치 크기(4)에서도 BatchNorm2d를 eval() 상태로 고정함으로써 사전학습된 정규화 통계량이 흔들리지 않고 안정적인 전이학습이 수행됨.
======================================================================================================================================================
"""