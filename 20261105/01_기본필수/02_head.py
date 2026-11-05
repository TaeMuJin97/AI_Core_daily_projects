"""
==============================================================================
[실습 보고서: 02_head.py - 사전학습 Backbone 동결 및 3클래스 분류 Head 교체]
1. 실험 목적: 사전학습된 특징 추출기(Backbone)의 가중치를 불러온 뒤 모든 파라미터를 동결(Freeze)하고,
              새로운 3클래스 분류용 Linear Head로 교체하여 Head-only 전이학습 구조를 검증함.
2. 고정 조건: 입력 규격([0, 1] 범위 RGB 32x32), Backbone 구조(Conv-BN-ReLU 2개 블록 + AdaptiveAvgPool2d(4, 4)),
              출력 클래스 수(3개: circle, square, triangle)
3. 핵심 구현: 
   - np.load(..., allow_pickle=False)를 통해 안전하게 수치 가중치만 로드하여 state_dict에 반영
   - 기존 모델의 전체 파라미터를 requires_grad=False로 동결한 뒤 model[9]를 nn.Linear(256, 3)으로 교체
   - 새로 생성된 Linear 층만 requires_grad=True가 되어 학습 파라미터 수가 정확히 771개(256*3 + 3)인지 확인
4. 주요 산출물: 
   - 콘솔 출력: 학습 가능 파라미터 수(TinyShapeCNN 771개, ResNet18 1,539개) 및 더미 입력에 대한 출력 Logit Shape (2, 3)
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

# 제공 부분: 0~8은 Backbone, 9는 새 3클래스 Head입니다.
# [핵심 포인트 1: AdaptiveAvgPool2d((4, 4))와 Flatten 차원 계산]
# 두 번째 Conv 블록의 출력 채널이 16개이고, AdaptiveAvgPool2d((4, 4))가 공간 해상도를 4x4로 고정하므로
# Flatten() 직후의 특징 벡터 차원은 16(채널) * 4(높이) * 4(너비) = 256차원이 됩니다.
model = nn.Sequential(
    nn.Conv2d(3, 8, 3, padding=1, bias=False), nn.BatchNorm2d(8), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, 3, padding=1, bias=False), nn.BatchNorm2d(16), nn.ReLU(),
    nn.AdaptiveAvgPool2d((4, 4)), nn.Flatten(), nn.Linear(256, 3),
)

# 안전한 수치 배열만 읽습니다. Target 이미지로 사전학습한 파일이 아닙니다.
# [새로 배운 개념: allow_pickle=False 보안 로드 및 부분 state_dict 업데이트]
# 임의 코드 실행 위험이 있는 파이썬 객체를 차단하고 순수 수치 배열(.npz)만 안전하게 읽어 들입니다.
# Backbone(0~8번 층)의 사전학습 가중치만 덮어쓰고, 다시 load_state_dict로 모델에 적용합니다.
with np.load(DATA / "source_backbone.npz", allow_pickle=False) as saved:
    state = model.state_dict()
    state.update({name: torch.from_numpy(saved[name].copy()) for name in saved.files})
model.load_state_dict(state)

# [핵심 포인트 2: Backbone 파라미터 동결(Freeze)]
# 먼저 모델의 모든 파라미터에 대해 역전파 기울기(Gradient) 계산을 비활성화합니다.
for p in model.parameters():
    p.requires_grad = False

# TODO B02: 256개 특징에서 3개 logit을 출력하는 새 Linear Head를 만드세요.
# BEGIN B02
# [핵심 포인트 3: 새로운 분류 Head 교체와 requires_grad 자동 활성화]
# 동결 루프 이후에 새로 생성하여 갈아끼운 nn.Linear(256, 3) 모듈은 기본적으로 requires_grad=True 상태입니다.
# 따라서 전체 모델 중 이 9번 층의 weight(256*3=768개)와 bias(3개)만 학습 대상이 됩니다.
model[9] = nn.Linear(256, 3)
# END B02

print("source 종류: 별도 합성 이미지로 사전학습한 TinyShapeCNN")
print("학습 파라미터:", sum(p.numel() for p in model.parameters() if p.requires_grad))
print("출력 shape:", tuple(model.eval()(torch.zeros(2, 3, 32, 32)).shape))

# PPT ResNet18의 구조도 다운로드 없이 확인합니다. 이것은 '전이학습 성능'이 아닙니다.
# [핵심 포인트 4: Torchvision ResNet18의 Head 교체 패턴 비교]
# Sequential 모델은 인덱스(model[9])로 접근하지만, ResNet18은 마지막 분류기 속성 이름이 .fc로 정의되어 있습니다.
# resnet.fc.in_features(512)를 동적으로 읽어와 하드코딩 없이 안전하게 3클래스 선형 층으로 교체합니다.
from torchvision.models import resnet18
resnet = resnet18(weights=None)
for p in resnet.parameters():
    p.requires_grad = False
resnet.fc = nn.Linear(resnet.fc.in_features, 3)
print("ResNet18 구조 확인용 Head 파라미터:", sum(p.numel() for p in resnet.parameters() if p.requires_grad))
print("주의: 위 ResNet18은 구조만 확인했습니다. ImageNet 학습 결과가 아닙니다.")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Head-only 전이학습의 학습 파라미터 수 검증:
   - TinyShapeCNN: Backbone(0~8번 층)은 모두 동결되고 새로 교체한 model[9] = nn.Linear(256, 3)만 열려 있어,
     학습 가능 파라미터 수가 256 * 3 (weight) + 3 (bias) = 771개로 정확히 산출됨.
   - ResNet18: 마지막 특징 차원(in_features=512)에서 3클래스로 가는 resnet.fc만 열려 있어,
     512 * 3 + 3 = 1,539개의 학습 파라미터가 확인됨.
2. 출력 텐서(Logit) Shape 확인:
   - 배치 크기 2인 더미 이미지(torch.zeros(2, 3, 32, 32)) 입력 시 출력 Shape가 (2, 3)으로 도출되어,
     샘플마다 3개 클래스에 대한 원점수(Logit)가 정상 출력됨을 검증함.
==============================================================================
"""