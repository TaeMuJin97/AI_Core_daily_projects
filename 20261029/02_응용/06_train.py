"""실습 06: 80 epoch 학습하고 10 epoch마다 같은 시점의 지표를 기록합니다."""

from pathlib import Path
import csv
import json
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

# 기본 경로 및 출력 폴더 설정
base = Path(__file__).resolve().parent
out = base / "outputs"
out.mkdir(exist_ok=True)

# 데이터 로드 및 전처리
# - CSV에서 train과 valid 데이터를 분리하여 읽어옵니다.
with (base / "data" / "points.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

train_rows = [r for r in rows if r["split"] == "train"]
valid_rows = [r for r in rows if r["split"] == "valid"]

# - 입력 특성(x1, x2)은 float32 실수 텐서로 변환
X_train = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in train_rows])

# - 분류 정답(label)은 CrossEntropyLoss 요구사항에 맞추어 torch.long(정수형)으로 변환
y_train = torch.tensor([int(r["label"]) for r in train_rows], dtype=torch.long)

X_valid = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in valid_rows])
y_valid = torch.tensor([int(r["label"]) for r in valid_rows], dtype=torch.long)

# test 40건은 모델에 전달하지 않습니다. 순서를 바꾸거나 다시 분할하지 않습니다.
# 시드 고정 및 디바이스(GPU/CPU) 결정
torch.manual_seed(42)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print("현재 사용 중인 장치:", device)  # GPU 사용 여부를 직접 확인하기 위한 출력

# DataLoader 구성 (미니배치 생성기)
# - generator에 고정 시드를 주어 미니배치 셔플 순서의 재현성을 보장합니다.
loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                    generator=torch.Generator().manual_seed(43), num_workers=0)

# 모델, 손실함수, 최적화기 정의
# - 2차원 입력 -> 8개 은닉 뉴런 -> ReLU 활성화 -> 2개 클래스 Logits 출력
# - .to(device)로 모델의 모든 가중치를 GPU/CPU 메모리로 이동시킵니다.
model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)).to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

# 평가 시 매번 장치 변환을 하지 않도록 전체 검증/훈련 텐서를 타겟 장치로 미리 복사
Xv, yv = X_valid.to(device), y_valid.to(device)
Xt, yt = X_train.to(device), y_train.to(device)
history = []

# =====================================================================
# 80 Epoch 학습 루프 (Training Loop)
# =====================================================================
for epoch in range(81):
    # epoch=0은 학습 전 모델의 초기 상태(Baseline)를 기록하기 위함
    if epoch > 0:
        # 모델을 학습 모드로 설정 (Dropout, BatchNorm 활성화)
        model.train()
        # DataLoader에서 미니배치(xb, yb)를 순회
        for xb, yb in loader:
            # 텐서와 모델의 장치(device)를 일치시킴
            xb, yb = xb.to(device), yb.to(device)
            # 1단계: 이전 스텝의 기울기 누적 방지를 위한 초기화
            optimizer.zero_grad()
            # 2단계: 순전파(Forward) 및 배치 손실 계산
            loss = loss_fn(model(xb), yb)
            # 현재 batch의 loss로 역전파하고 optimizer를 한 번 갱신하세요.
            # zero_grad와 순전파·손실 계산은 위에 제공되어 있습니다.
            # >>> A06
            # TODO A06: 위 요구사항을 읽고 이 블록을 완성하세요.
            # 3단계: 역전파(Backpropagation) - 연산 그래프를 역추적하여 w.grad 계산
            loss.backward()
            # 4단계: 가중치 갱신(Optimizer Step) - W = W - lr * W.grad
            optimizer.step()
            # <<< A06
    
    # =====================================================================
    # 10 Epoch마다 평가 및 로깅 (Evaluation & Logging)
    # =====================================================================
    # epoch=0은 학습 전입니다. 로그는 갱신이 끝난 동일 모델로 측정합니다.
    if epoch % 10 == 0:
        # 평가 모드 전환 (평가 시 동작이 달라지는 레이어 제어)
        model.eval()
        # 평가 구간에서는 기울기 연산 그래프 생성을 차단하여 메모리와 연산 절약
        with torch.no_grad():
            # 훈련 손실 측정
            train_loss = loss_fn(model(Xt), yt).item()
            
            # 검증 데이터 추론 및 손실 계산
            logits = model(Xv)
            valid_loss = loss_fn(logits, yv).item()
            
            # 정확도 계산: argmax(dim=1)로 예측 클래스 번호를 뽑아 일치 여부 평균 계산
            accuracy = (logits.argmax(dim=1) == yv).float().mean().item()
            
        history.append([epoch, train_loss, valid_loss, accuracy])
        print(epoch, round(train_loss, 6), round(valid_loss, 6), round(accuracy, 4))


with (out / "training_history.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "train_loss_eval", "valid_loss", "valid_accuracy"])
    writer.writerows(history)



# 학습 지표 해석 (06 실습 결과)
# Epoch 0 (0.565 -> 0.700): 
# 학습 전 초기 가중치 상태에서의 기본 성능입니다.
# Epoch 30 이후 (0.176 -> 1.000): 
# 검증 정확도(valid_accuracy)가 1.0(100%)에 도달했으며, 
# 손실(valid_loss) 또한 꾸준히 우하향하여 안정적으로 수렴함을 보여줍니다.