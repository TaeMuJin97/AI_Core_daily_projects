"""
==============================================================================
[실습 보고서: 05_errors.py - 오분류(Error) 샘플 자동 추출 및 시각화 오류 갤러리 구축]
1. 실험 목적: 검증 셋(valid) 전체에 대해 모델 추론을 수행한 뒤, 실제 정답(y_valid)과 예측값(predictions)이
              다른 오답 샘플들의 인덱스를 추출하고, PIL을 이용해 원본 이미지 하단에 실제 레이블, 예측 레이블,
              그리고 모델의 확신도(Confidence, Softmax 최댓값)를 기재한 오분류 시각화 이미지 및 CSV 리포트를 생성함.
2. 고정 조건: 난수 시드(seed=14), 학습 횟수(8 Epochs), 최대 시각화 샘플 수(최대 8장), 타일 해상도(192x240)
3. 핵심 구현: 
   - predictions != y_valid 비교 연산을 통한 오답 샘플 인덱스(indices) 추출
   - Pillow(Image, ImageDraw) 라이브러리를 활용해 오답 이미지 하단에 True/Pred/Confidence 텍스트 오버레이 시각화
   - outputs/errors.csv 파일로 오분류 파일명, 실제 정답 클래스, 예측 클래스, 확신도 기록
4. 주요 산출물: 
   - outputs/error_*.png (최대 8장의 오분류 타일 시각화 이미지)
   - outputs/errors.csv (오분류 상세 메타데이터 기록표)
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
from PIL import Image, ImageDraw
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

# TODO A05: 실제값과 예측값이 다른 행의 인덱스를 구하세요.
# BEGIN A05
# [핵심 포인트 1: 오분류(Error) 샘플 인덱스 추출]
# 실제 정답 텐서(y_valid)와 모델 예측 텐서(predictions)가 같지 않은(!=) 위치의 인덱스를 찾아 파이썬 리스트로 변환합니다.
indices = (predictions != y_valid).nonzero(as_tuple=True)[0].tolist()  # 예측과 실제가 다른 인덱스를 구하세요.
# END A05

records = []
for old in OUT.glob("error_*.png"):
    old.unlink()

# [핵심 포인트 2: 오분류 갤러리(Error Gallery) 시각화 및 메타데이터 기록]
# 틀린 샘플 중 최대 8장을 골라 원본 이미지를 불러온 뒤, 하단에 흰색 여백(Tile)을 붙이고
# 실제 정답(true), 예측 클래스(pred), 모델이 확신했던 확률(p, Confidence)을 텍스트로 적어 저장합니다.
for i in indices[:8]:
    image = Image.open(valid.samples[i][0]).convert("RGB").resize((192, 192))
    tile = Image.new("RGB", (192, 240), "white")
    tile.paste(image, (0, 0))
    draw = ImageDraw.Draw(tile)
    
    draw.text((5, 195), f"true: {valid.classes[y_valid[i]]}", fill="black")
    draw.text((5, 210), f"pred: {valid.classes[predictions[i]]}", fill="black")
    draw.text((5, 225), f"p={probabilities[i].max().item():.3f}", fill="black")
    
    tile.save(OUT / f"error_{i:03d}.png")
    records.append({
        "file": Path(valid.samples[i][0]).name,
        "actual": int(y_valid[i]),
        "predicted": int(predictions[i]),
        "confidence": probabilities[i].max().item()
    })

pd.DataFrame(records, columns=["file", "actual", "predicted", "confidence"]).to_csv(OUT / "errors.csv", index=False)
print("전체 오답:", len(indices), "저장:", len(records), "없으면 생성하지 않음")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 오분류 분석(Error Analysis) 자동화 검증:
   - Confusion Matrix나 숫자 지표를 넘어서 모델이 어떤 샘플에서 헷갈렸는지 시각적 이미지(error_*.png)와 CSV로 직관적 확인 가능.
2. 확신도(Confidence) 분석의 의의:
   - 오답 샘플임에도 모델이 높은 확률(예: p=0.95 이상)로 틀렸는지, 아니면 애매하게(p=0.34 등) 틀렸는지를 파악하여
     데이터 오라벨(Mislabeling) 여부나 모델의 과신(Overconfidence) 현상을 진단하는 기초 자료로 활용함.
==============================================================================
"""