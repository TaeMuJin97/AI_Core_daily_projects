"""
==============================================================================
[실습 보고서: 07_project.py - 응용 전이학습 전략 및 클래스 불균형 대응 3가지 조건 비교 자동화 파이프라인]
1. 실험 목적: Head-only, Partial, 그리고 Head + Class Weight의 3가지 핵심 실험 군을
              동일한 조건(seed=14, 8 Epochs)에서 비교하고, Validation Loss 기준 Best Checkpoint를
              복원하여 성능 지표(metrics.csv/history.csv/predictions.csv/confusion.csv)와
              마지막 조건의 대표 오답 Grad-CAM(project_cam.png)을 자동 생성함.
2. 고정 조건: 난수 시드(seed=14), 입력 규격(32x32 RGB, [0, 1]), Optimizer(AdamW, lr=0.003, weight_decay=0.0001),
              총 8 Epochs, Test 분할 미사용(test_used=False)
3. 핵심 구현: 
   - A07: experiments 리스트에 3가지 비교 전략 정의
   - A08: valid.samples 순서에 맞춰 실제값, 예측값, 확신도(Confidence)가 담긴 정밀 예측 로그 테이블 생성
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
import cv2

train = ImageFolder(DATA / "train", transform=transform)
valid = ImageFolder(DATA / "valid", transform=transform)

# [핵심 개념: 인메모리 텐서 스택 구성]
# 개별 이미지 튜플을 torch.stack으로 묶어 [N, 3, 32, 32] 형태의 일괄 배치 텐서로 변환합니다.
X_train = torch.stack([train[i][0] for i in range(len(train))])
y_train = torch.tensor(train.targets, dtype=torch.long)
X_valid = torch.stack([valid[i][0] for i in range(len(valid))])
y_valid = torch.tensor(valid.targets, dtype=torch.long)

# TODO A07: Head 기준선·Partial·Head+weight 세 조건을 고정하세요.
# BEGIN A07
# [핵심 개념: 비교 실험 군(Experiments) 확장 설계]
# 1) head+none: 분류기만 학습하는 기본 전이학습 기준선
# 2) partial+none: 상위 특징 추출 층(model[4])까지 함께 열어 미세조정하는 범위 확장 전략
# 3) head+weight: 불균형 데이터 해소를 위해 CrossEntropyLoss에 역빈도 가중치를 부여한 보정 전략
experiments = [
    ("head", "none"),
    ("partial", "none"),
    ("head", "weight")
]
# END A07

rows = []
all_history = []

for strategy, balance in experiments:
    # [핵심 개념: 루프 내부 시드 고정으로 공정한 조건 유지]
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

    # [핵심 개념: 학습 범위(Requires_grad) 동적 제어]
    for p in model.parameters():
        p.requires_grad = False
    for p in model[9].parameters():
        p.requires_grad = True
    if strategy == "partial":
        for p in model[4].parameters():
            p.requires_grad = True
            
    # BatchNorm 통계를 고정하기 위해 eval() 모드 지정 (가중치 업데이트와 무관하게 러닝 통계 보호)
    model.eval()
    
    # 오직 requires_grad=True인 파라미터만 Optimizer에 전달하여 불필요한 연산 차단
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=0.003, weight_decay=0.0001)
    
    # [핵심 개념: 클래스 불균형 해소를 위한 역빈도(Inverse Frequency) 가중치 산출]
    counts = torch.bincount(y_train, minlength=3).float()
    inverse = 1.0 / counts
    class_weights = inverse / inverse.mean()
    
    # balance 조건에 따라 Loss에 가중치(weight)를 동적으로 부여
    criterion = nn.CrossEntropyLoss(weight=class_weights if balance == "weight" else None)
    
    best_loss = float("inf")
    started = time.perf_counter()
    
    for epoch in range(1, 9):
        optimizer.zero_grad()
        loss = criterion(model(X_train), y_train)
        loss.backward()
        optimizer.step()
        
        with torch.no_grad():
            vl = criterion(model(X_valid), y_valid).item()
            
        all_history.append({"strategy": strategy, "balance": balance, "epoch": epoch, "valid_loss": vl})
        
        # [핵심 개념: Validation Loss 기준 Best Model Checkpointing]
        # 에폭 8까지 학습하는 동안 검증 손실이 가장 낮았던 순간의 가중치를 deepcopy(.detach().clone())로 백업
        if vl < best_loss:
            best_loss = vl
            best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            
    elapsed = time.perf_counter() - started
    
    # 평가 전 가장 성능이 뛰어났던 에폭의 가중치로 모델 복원
    model.load_state_dict(best_state)
    
    with torch.no_grad():
        prob = model(X_valid).softmax(1)
        pred = prob.argmax(1)
        
    report = classification_report(y_valid, pred, labels=[0, 1, 2], output_dict=True, zero_division=0)
    
    rows.append({
        "strategy": strategy,
        "balance": balance,
        "params": sum(p.numel() for p in model.parameters() if p.requires_grad),
        "best_epoch": best_epoch,
        "accuracy": accuracy_score(y_valid, pred),
        "macro_f1": f1_score(y_valid, pred, labels=[0, 1, 2], average="macro", zero_division=0),
        "triangle_recall": report['2']['recall'],
        "seconds": elapsed
    })

pd.DataFrame(rows).to_csv(OUT / "metrics.csv", index=False)
pd.DataFrame(all_history).to_csv(OUT / "history.csv", index=False)

# 마지막 head+weight 후보의 예측을 설명용으로 저장합니다. 자동 최고 모델이라고 부르지 않습니다.
# TODO A08: 실제 y_valid와 pred를 표에 넣으세요. valid.samples와 같은 순서입니다.
# BEGIN A08
# [핵심 개념: 샘플별 정밀 예측 이력 데이터프레임 구성]
# 파일 이름, 실제 라벨(actual), 모델 예측값(predicted), 그리고 확신도(confidence)를 매핑하여 로그 저장
result = pd.DataFrame({
    "file": [Path(p).name for p, _ in valid.samples],
    "actual": y_valid.numpy(),
    "predicted": pred.numpy(),
    "confidence": prob.max(1).values.numpy()
})
# END A08

result.to_csv(OUT / "predictions.csv", index=False)
pd.DataFrame(confusion_matrix(y_valid, pred, labels=[0, 1, 2]), index=valid.classes, columns=valid.classes).to_csv(OUT / "confusion.csv")

predictions = pred
probabilities = prob

for old in OUT.glob("project_error_*.png"):
    old.unlink()
    
errors = (pred != y_valid).nonzero().flatten().tolist()
for i in errors[:8]:
    rgb = np.uint8(X_valid[i].permute(1, 2, 0).numpy() * 255)
    cv2.imwrite(str(OUT / f"project_error_{i:03d}.png"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    
index = errors[0] if errors else 0

# [핵심 개념: autograd.grad를 이용한 특정 클래스 Logit의 공간 편미분 (Grad-CAM)]
# Hook 없이 Sequential을 둘로 나누어 첫 번째 오답 샘플에 대한 모델의 시각적 판단 근거 역추적
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

cv2.imwrite(str(OUT / "project_cam.png"), cv2.resize(overlay, (256, 256)))

print(pd.DataFrame(rows).drop(columns="seconds").round(4).to_string(index=False))
print("예측 행:", len(result), "오답:", len(errors), "test 사용: False")