
"""
Day14 실습: Grad-CAM을 활용한 CNN 모델의 판단 영역 시각화

[실습 목적]
CNN 모델이 이미지를 분류할 때 어떤 영역이 예측 결과에 기여했는지
Grad-CAM(Gradient-weighted Class Activation Mapping)으로 시각화합니다.

[주요 동작]
1. Train/Valid 이미지 로딩 및 32×32 RGB Tensor 변환
2. TinyShapeCNN 생성 및 사전학습된 Backbone 가중치 불러오기
3. Backbone을 동결하고 분류 Head만 1 Epoch 학습
4. 검증 데이터에서 정답·오답 사례를 각각 최대 1개 선택
5. 마지막 특징 추출 계층의 Feature Map과 Gradient 계산
6. Grad-CAM 생성 후 원본 이미지와 Heatmap 합성
7. cam_correct.png, cam_wrong.png 파일 저장

[주의사항]
- Test 데이터는 사용하지 않습니다.
- Grad-CAM은 예측에 기여한 영역을 시각화하는 설명 기법입니다.
- Heatmap이 밝다고 해서 해당 영역이 반드시 정답의 원인인 것은 아닙니다.
- 정답 또는 오답 사례가 없다면 해당 이미지를 생성하지 않습니다.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
from torch import nn
from torchvision.datasets import ImageFolder
from torchvision import transforms as tr
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import cv2


# ============================================================
# 1. 실행 환경 및 경로 설정
# ============================================================

torch.set_num_threads(1)
torch.manual_seed(14)

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE


# ============================================================
# 2. 이미지 데이터 로딩 및 전처리
# ============================================================

# RGB 이미지를 32×32 크기로 변환하고 픽셀값을 [0,1]로 변환
transform = tr.Compose([
    tr.Resize((32, 32)),
    tr.ToTensor()
])

# Train/Valid 데이터 로딩 (Test 데이터는 사용하지 않음)
train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)

# 이미지와 정답 라벨을 Tensor로 구성
X_train = torch.stack([train[i][0] for i in range(len(train))])
y_train = torch.tensor(train.targets, dtype=torch.long)

X_valid = torch.stack([valid[i][0] for i in range(len(valid))])
y_valid = torch.tensor(valid.targets, dtype=torch.long)


# ============================================================
# 3. CNN 모델 생성
# ============================================================

model = nn.Sequential(

    # [Stage 1] 기초 특징 추출
    nn.Conv2d(3, 8, 3, padding=1, bias=False),  # [0]
    nn.BatchNorm2d(8),                          # [1]
    nn.ReLU(),                                  # [2]
    nn.MaxPool2d(2),                            # [3]

    # [Stage 2] 마지막 특징 추출 Stage
    nn.Conv2d(8, 16, 3, padding=1, bias=False), # [4]
    nn.BatchNorm2d(16),                         # [5]
    nn.ReLU(),                                  # [6]

    # [특징 집약] 특징맵을 256차원 벡터로 변환
    nn.AdaptiveAvgPool2d((4, 4)),               # [7]
    nn.Flatten(),                               # [8]

    # [Head] 3개 클래스 분류
    nn.Linear(256, 3)                           # [9]
)


# ============================================================
# 4. 사전학습된 Backbone 가중치 불러오기
# ============================================================

# 별도의 합성 이미지로 사전학습된 가중치를 불러옴
# Target 이미지로 사전학습한 모델이 아님
with np.load(DATA / "source_backbone.npz", allow_pickle=False) as saved:
    state = model.state_dict()
    state.update({
        name: torch.from_numpy(saved[name].copy())
        for name in saved.files
    })

model.load_state_dict(state)


# ============================================================
# 5. Backbone 동결 및 Head 학습 설정
# ============================================================

# 모든 파라미터 동결
for p in model.parameters():
    p.requires_grad = False

# 마지막 분류 Head만 학습 가능하도록 설정
for p in model[9].parameters():
    p.requires_grad = True

# BatchNorm Running Mean/Var를 고정하기 위해 평가 모드 사용
# eval() 상태에서도 Gradient 계산 및 Head 학습은 가능
model.eval()

# Head만 학습하도록 Optimizer 설정
optimizer = torch.optim.AdamW(
    model[9].parameters(),
    lr=0.01,
    weight_decay=0.0
)

criterion = nn.CrossEntropyLoss()


# ============================================================
# 6. Head Only 학습 (1 Epoch)
# ============================================================

# 모델의 초기 오분류 사례를 관찰하기 위한 1회 학습
for epoch in range(1):

    optimizer.zero_grad()

    # 순전파 및 손실 계산
    loss = criterion(model(X_train), y_train)

    # 역전파 및 Head 가중치 갱신
    loss.backward()
    optimizer.step()


# ============================================================
# 7. 검증 데이터 예측
# ============================================================

# 검증 데이터에 대해 클래스별 Logit과 예측 라벨 계산
with torch.no_grad():
    logits = model(X_valid)
    probabilities = logits.softmax(dim=1)
    predictions = logits.argmax(dim=1)


# ============================================================
# 8. 정답 및 오답 사례 선택
# ============================================================

selected = []

# 정답(correct)과 오답(wrong)에서 각각 최대 1개 선택
for kind, mask in [
    ("correct", predictions == y_valid),
    ("wrong", predictions != y_valid)
]:

    # 조건에 해당하는 이미지 인덱스 추출
    indices = mask.nonzero().flatten().tolist()

    if indices:
        # 해당하는 첫 번째 이미지 선택
        selected.append((kind, indices[0]))
    else:
        # 사례가 없으면 임의로 생성하지 않음
        print(kind, "사례 없음: 지표 그대로 보고")


# ============================================================
# 9. Grad-CAM 생성 및 시각화
# ============================================================

for kind, index in selected:

    # --------------------------------------------------------
    # 9-1. Grad-CAM 분석용 이미지 준비
    # --------------------------------------------------------

    # 선택한 이미지 1개를 Batch 형태로 추출
    # requires_grad=True: 입력으로부터 Gradient 계산 가능
    image = X_valid[index:index + 1].clone().requires_grad_(True)

    # --------------------------------------------------------
    # 9-2. 마지막 특징 추출 계층의 Feature Map 계산
    # --------------------------------------------------------

    # Stage 1 + Stage 2의 출력 Feature Map 추출
    # model[:7] → Conv, BN, ReLU 등 특징 추출 계층
    #
    # Feature Shape: [1, 16, 16, 16]
    features = model[:7](image)

    # Feature Map을 분류 Head까지 전달하여 Logit 계산
    # model[7:] → AdaptiveAvgPool + Flatten + Linear
    one = model[7:](features)

    # 가장 높은 Logit을 가진 예측 클래스 선택
    target = int(one.argmax(1).item())

    # --------------------------------------------------------
    # 9-3. 예측 클래스에 대한 Gradient 계산
    # --------------------------------------------------------

    # 예측 클래스의 Logit을 Feature Map에 대해 미분
    # 각 Feature가 해당 클래스 점수에 얼마나 민감한지 계산
    gradient = torch.autograd.grad(
        one[0, target],
        features
    )[0]

    # --------------------------------------------------------
    # 9-4. 채널별 중요도 가중치 계산
    # --------------------------------------------------------

    # Gradient의 공간 차원(H,W)에 대해 평균 계산
    # 각 Feature Map 채널의 중요도 가중치를 구함
    #
    # gradient Shape: [1, 16, 16, 16]
    # weights Shape : [1, 16, 1, 1]
    weights = gradient.mean(
        dim=(2, 3),
        keepdim=True
    )

    # --------------------------------------------------------
    # 9-5. Grad-CAM 생성
    # --------------------------------------------------------

    # Feature Map에 채널별 가중치를 곱한 후 채널 방향으로 합산
    #
    # ReLU:
    # 예측 클래스 점수에 대한 양의 기여만 남김
    # 음수 반응은 0으로 처리
    cam = (weights * features).sum(dim=1).relu()

    # --------------------------------------------------------
    # 9-6. Heatmap 크기 복원 및 정규화
    # --------------------------------------------------------

    # Feature Map 크기 16×16 → 입력 이미지 크기 32×32
    # Bilinear Interpolation으로 부드럽게 확대
    cam = torch.nn.functional.interpolate(
        cam.unsqueeze(1),
        size=(32, 32),
        mode="bilinear",
        align_corners=False
    )[0, 0].detach().numpy()

    # Heatmap 값을 0~1 범위로 정규화
    # 1e-8: 모든 값이 0일 때 0으로 나누는 오류 방지
    cam = cam / max(float(cam.max()), 1e-8)

    # --------------------------------------------------------
    # 9-7. 원본 이미지 및 Heatmap 생성
    # --------------------------------------------------------

    # PyTorch Tensor [C,H,W] → 이미지 [H,W,C]로 변환
    # [0,1] 픽셀값을 [0,255] uint8로 복원
    rgb = (
        X_valid[index]
        .permute(1, 2, 0)
        .numpy() * 255
    ).astype(np.uint8)

    # Grad-CAM 값을 JET ColorMap으로 변환
    # 상대적으로 높은 값은 따뜻한 색, 낮은 값은 차가운 색으로 표시
    heat = cv2.applyColorMap(
        np.uint8(cam * 255),
        cv2.COLORMAP_JET
    )

    # --------------------------------------------------------
    # 9-8. 원본 이미지와 Heatmap 합성
    # --------------------------------------------------------

    # 원본 이미지 60% + Heatmap 40% 합성
    # cv2는 BGR 순서를 사용하므로 RGB → BGR 변환
    overlay = cv2.addWeighted(
        cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
        0.6,
        heat,
        0.4,
        0
    )

    # --------------------------------------------------------
    # 9-9. Grad-CAM 결과 이미지 저장
    # --------------------------------------------------------

    # 결과를 256×256으로 확대하여 PNG 저장
    # cam_correct.png 또는 cam_wrong.png 생성
    cv2.imwrite(
        str(OUT / f"cam_{kind}.png"),
        cv2.resize(overlay, (256, 256))
    )

    # 분석 대상과 Heatmap 크기 출력
    print(
        kind,
        Path(valid.samples[index][0]).name,
        "target:", valid.classes[target],
        "CAM:", cam.shape
    )


# ============================================================
# 10. 해석 시 주의사항
# ============================================================

# Grad-CAM은 모델이 예측 클래스 점수를 계산할 때
# 어떤 공간 영역의 Feature가 양의 기여를 하는지 보여주는 기법
#
# 단, 강조된 영역이 실제 인과관계나 정답의 근거임을
# 증명하는 것은 아니며 추가 분석이 필요함