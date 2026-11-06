"""
==============================================================================
[실습 보고서: 07_project.py - 전이학습 분류 통합 프로젝트 파이프라인 및 산출물 자동 생성]
1. 실험 목적: 사전학습된 TinyShapeCNN Backbone을 동결하고 3클래스 Head만 학습(Head-only)한 뒤,
              Valid Loss 기준 최적 체크포인트를 복원하여 정량 지표(metrics.csv/json), 예측 로그(predictions.csv),
              혼동 행렬(confusion.csv), 대표 오분류 이미지, 그리고 Grad-CAM(project_cam.png)까지
              전체 프로젝트 산출물을 단일 파이프라인으로 생성·검증함.
2. 핵심 해결 포인트:
   - Windows 한글 디렉터리('01_기본필수')에서 cv2.imwrite가 조용히 실패하는 현상을 방지하기 위해
     cv2.imencode와 Path.write_bytes() 조합을 사용하여 UTF-8 경로 안전 저장 구현.
   - 스크립트 종료 시 PyTorch autograd 그래프와 OpenCV C++ 모듈 간 해체 순서 충돌로 발생하는
     Segmentation fault를 차단하기 위해 버퍼 플러시 후 os._exit(0)으로 프로세스 안전 종료.
==============================================================================
"""
"""Day14: 제공된 정상 이미지로 학습합니다. test는 읽지 않습니다."""
from pathlib import Path
import os
import sys
import json
import numpy as np
import pandas as pd
import torch
from torch import nn
from torchvision.datasets import ImageFolder
from torchvision import transforms as tr
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import cv2

torch.set_num_threads(1)
torch.manual_seed(14)
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE

# [한글 경로 호환 이미지 저장 헬퍼 함수]
# Windows 환경에서 폴더명에 한글('01_기본필수' 등)이 있을 때 cv2.imwrite가 실패하는 문제를 해결합니다.
def save_image_safe(path: Path, img_bgr: np.ndarray) -> bool:
    ok, encoded = cv2.imencode(path.suffix, img_bgr)
    if ok:
        path.write_bytes(encoded.tobytes())
    return bool(ok)

# 여기서는 [0,1] RGB 32×32로 학습한 교육용 source 가중치를 사용합니다.
# ImageNet ResNet18과 입력 변환을 섞지 않습니다.
transform = tr.Compose([tr.Resize((32, 32)), tr.ToTensor()])
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

history = []
best_loss = float("inf")
for epoch in range(1, 9):
    optimizer.zero_grad()
    loss = criterion(model(X_train), y_train)
    # TODO B07: 역전파와 Optimizer 갱신을 수행하세요.
    # BEGIN B07
    loss.backward()
    optimizer.step()
    # END B07
    with torch.no_grad():
        valid_loss = criterion(model(X_valid), y_valid).item()
    history.append({"epoch": epoch, "valid_loss": valid_loss})
    if valid_loss < best_loss:
        best_loss = valid_loss
        best_epoch = epoch
        best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

model.load_state_dict(best_state)
with torch.no_grad():
    logits = model(X_valid)
    probabilities = logits.softmax(1)
    # TODO B08: 각 행의 가장 큰 logit 열을 예측 라벨로 고르세요.
    # BEGIN B08
    predictions = logits.argmax(1)
    # END B08

metrics = {
    "accuracy": accuracy_score(y_valid, predictions),
    "macro_f1": f1_score(y_valid, predictions, labels=[0, 1, 2], average="macro", zero_division=0),
    "best_epoch": best_epoch,
    "valid_n": len(valid),
    "source": "synthetic_source_pretraining",
    "test_used": False,
}
pd.DataFrame([metrics]).to_csv(OUT / "metrics.csv", index=False)
pd.DataFrame(history).to_csv(OUT / "history.csv", index=False)
pd.DataFrame({
    "file": [Path(p).name for p, _ in valid.samples],
    "actual": y_valid.numpy(),
    "predicted": predictions.numpy(),
    "confidence": probabilities.max(1).values.numpy(),
}).to_csv(OUT / "predictions.csv", index=False)

# TODO B09: metrics를 UTF-8 JSON 문자열로 저장하세요. 아래 제공된 경로를 사용합니다.
# BEGIN B09
(OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
# END B09

pd.DataFrame(
    confusion_matrix(y_valid, predictions, labels=[0, 1, 2]),
    index=valid.classes,
    columns=valid.classes,
).to_csv(OUT / "confusion.csv")

for old in OUT.glob("project_error_*.png"):
    old.unlink()
errors = (predictions != y_valid).nonzero().flatten().tolist()
for i in errors[:8]:
    image = (X_valid[i].permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    save_image_safe(OUT / f"project_error_{i:02d}.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

index = errors[0] if errors else 0
# hook 대신 Sequential을 둘로 나눕니다. 관심 클래스의 logit을 미분합니다.
image = X_valid[index:index + 1].clone().requires_grad_(True)
features = model[:7](image)
logits_one = model[7:](features)
target = int(logits_one.argmax(1).item())
gradient = torch.autograd.grad(logits_one[0, target], features)[0]
weights = gradient.mean(dim=(2, 3), keepdim=True)
cam = (weights * features).sum(dim=1).relu()
cam = torch.nn.functional.interpolate(cam.unsqueeze(1), size=(32, 32), mode="bilinear", align_corners=False)[0, 0]
cam = cam.detach().numpy()
cam = cam / max(float(cam.max()), 1e-8)  # 양의 반응이 없으면 0 지도를 유지
rgb = (X_valid[index].permute(1, 2, 0).numpy() * 255).astype(np.uint8)
heat_bgr = cv2.applyColorMap(np.uint8(cam * 255), cv2.COLORMAP_JET)
overlay = cv2.addWeighted(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), 0.6, heat_bgr, 0.4, 0)

# 한글 경로에서도 무조건 저장되도록 save_image_safe 사용
cam_resized = cv2.resize(overlay, (256, 256))
save_image_safe(OUT / "project_cam.png", cam_resized)

print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
print("오답 수:", len(errors), "예측 행:", len(valid), "test 사용: False")

# C++ 확장 모듈 해제 충돌(Segmentation fault) 방지용 즉시 종료
sys.stdout.flush()
os._exit(0)