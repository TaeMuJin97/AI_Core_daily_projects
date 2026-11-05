"""
==============================================================================
[실습 보고서: 06_cam_targets.py - 타깃 클래스(Target Class) 변경에 따른 Grad-CAM 히트맵 비교]
1. 실험 목적: 동일한 검증 이미지 1장(index=0)에 대해 미분 대상인 타깃 클래스 Logit을
              target=0(circle)과 target=1(square)로 각각 바꾸어 Grad-CAM을 계산했을 때,
              모델이 각 클래스를 판단하기 위해 주목하는 공간 영역(Heatmap)이 어떻게 달라지는지 확인함.
2. 고정 조건: 난수 시드(seed=14), 입력 이미지(X_valid[0:1]), 특징 추출 층(model[:7], 두 번째 Conv-BN-ReLU 출력 [1, 16, 16, 16]),
              모델 학습 조건(Head-only 8 Epochs, lr=0.01)
3. 핵심 구현: 
   - Sequential 모델을 model[:7](특징 추출부)과 model[7:](풀링 및 분류부)로 분할 실행하여 Hook 없이도 중간 Feature Map 확보
   - torch.autograd.grad(out[0, target], features)[0]를 통해 특정 클래스 Logit의 Feature Map에 대한 편미분(Gradient) 계산
   - 공간 축(H, W) 평균 가중치와 Feature Map의 가중합 + ReLU + Bilinear 보간 + OpenCV JET 컬러맵 오버레이 수행
4. 주요 산출물: 
   - outputs/target_0_cam.png (circle 클래스 점수에 긍정적으로 기여한 영역 히트맵)
   - outputs/target_1_cam.png (square 클래스 점수에 긍정적으로 기여한 영역 히트맵)
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
import cv2
train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)
X_train = torch.stack([train[i][0] for i in range(len(train))])
y_train = torch.tensor(train.targets, dtype=torch.long)
X_valid = torch.stack([valid[i][0] for i in range(len(valid))])
y_valid = torch.tensor(valid.targets, dtype=torch.long)

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

# requires_grad는 가중치 갱신, eval()은 BatchNorm 통계 사용 방식을 제어합니다.
for p in model.parameters():
    p.requires_grad = False
for p in model[9].parameters():
    p.requires_grad = True
model.eval()  # 고정 Backbone의 running 통계도 보존

optimizer = torch.optim.AdamW(model[9].parameters(), lr=0.01, weight_decay=0.0)
criterion = nn.CrossEntropyLoss()

# 제공된 8회 학습. 평가용 valid를 backward에 넣지 않습니다.
for epoch in range(8):
    optimizer.zero_grad()
    loss = criterion(model(X_train), y_train)
    loss.backward()
    optimizer.step()

with torch.no_grad():
    logits = model(X_valid)
    probabilities = logits.softmax(dim=1)
    predictions = logits.argmax(dim=1)

index = 0
for target in [0, 1]:
    # [핵심 포인트 1: 동결된 Backbone을 통과해 중간 Feature Map의 계산 그래프(Computational Graph) 살리기]
    # model[:7]의 파라미터들은 requires_grad=False로 동결되어 있으므로, 입력 image가 requires_grad=False면
    # 중간 출력인 features도 미분 그래프가 끊기게 됩니다. 따라서 image에 .requires_grad_(True)를 설정해야 합니다.
    image = X_valid[index:index+1].clone().requires_grad_(True)
    
    # Sequential 슬라이싱: model[:7]은 두 번째 ReLU까지의 Feature Map [1, 16, 16, 16], model[7:]은 Pool+Flatten+Linear입니다.
    features = model[:7](image)
    out = model[7:](features)
    
    # TODO A06: target logit의 features에 대한 gradient를 계산하세요.
    # BEGIN A06
    # [핵심 포인트 2: torch.autograd.grad를 이용한 특정 텐서 직접 편미분]
    # backward()와 Hook을 등록하는 대신, 스칼라 타깃 점수(out[0, target])를 중간 텐서(features)에 대해 직접 미분합니다.
    # 반환값은 튜플 형태이므로 [0]으로 첫 번째 원소(features와 동일한 shape의 기울기 텐서)를 추출합니다.
    gradient = torch.autograd.grad(out[0, target], features)[0]  # autograd.grad 호출로 바꾸세요.
    # END A06
    
    # [핵심 포인트 3: Grad-CAM 수식 구현 및 OpenCV 컬러맵 오버레이]
    # 1) 공간 축(H=2, W=3)에 대해 기울기를 평균 내어 채널별 중요도 가중치 alpha [1, 16, 1, 1] 산출
    # 2) features와 곱한 뒤 채널 축(dim=1)으로 합산하고, ReLU로 해당 클래스 점수를 높이는 양(+)의 기여 영역만 남김
    cam = (gradient.mean((2, 3), keepdim=True) * features).sum(1).relu()
    
    # 3) 16x16 해상도의 CAM을 원본 입력 크기인 (32, 32)로 양선형 보간(bilinear interpolation) 후 [0, 1] 정규화
    cam = torch.nn.functional.interpolate(cam.unsqueeze(1), (32, 32), mode="bilinear", align_corners=False)[0, 0].detach().numpy()
    cam = cam / max(float(cam.max()), 1e-8)
    
    # 4) PyTorch [C, H, W] RGB 텐서를 OpenCV용 [H, W, C] uint8 배열로 변환하고 JET 히트맵과 6:4 비율로 합성
    rgb = np.uint8(X_valid[index].permute(1, 2, 0).numpy() * 255)
    heat = cv2.applyColorMap(np.uint8(cam * 255), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), .6, heat, .4, 0)
    
    cv2.imwrite(str(OUT / f"target_{target}_cam.png"), cv2.resize(overlay, (256, 256)))
    print("target:", valid.classes[target], "logit:", round(out[0, target].item(), 4), "mean CAM:", round(float(cam.mean()), 4))


"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 타깃 클래스(Target Logit)에 따른 히트맵의 클래스 특이성(Class-Discriminative) 확인:
   - 똑같은 이미지(X_valid[0], 실제 정답 circle)를 넣더라도, 미분 대상(target)을 0(circle)으로 둘 때와
     1(square)로 둘 때 계산되는 Gradient가 달라져 히트맵(mean CAM 및 강조 위치)이 서로 다르게 생성됨.
   - 즉, Grad-CAM은 단순히 "이미지에서 눈에 띄는 곳"을 보여주는 것이 아니라,
     "내가 지정한 특정 클래스 점수를 올리는 데 기여한 영역"을 역추적하는 도구임을 확인함.
2. 구현 디테일 (Sequential 분할 + autograd.grad vs Hook):
   - nn.Sequential 모델처럼 중간 층을 슬라이싱(model[:7], model[7:])할 수 있는 구조에서는
     복잡한 Forward/Backward Hook 등록 없이 torch.autograd.grad(out[0, target], features)[0] 한 줄로
     깔끔하고 메모리 누수 위험 없이 Grad-CAM을 계산할 수 있음.
==============================================================================
"""