# ==============================================================================
# [실습 보고서: 05_dropout.py - Dropout 적용 여부에 따른 과적합 억제 및 모드 비교]
# 1. 실험 목적: 학습 중 일부 뉴런을 무작위로 비활성화하는 Dropout(p=0.0 vs p=0.3)이 
#               과적합(Overfitting)을 어떻게 늦추고 일반화 성능을 개선하는지 비교[cite: 8, 58, 66]
# 2. 고정 조건: 데이터 분할(Split), Seed(42/43), 모델 폭(width=32), Optimizer(AdamW), lr(0.01), Epochs(40)[cite: 115]
# 3. 변경 조건: Dropout 확률 (p = 0.0 vs p = 0.3)[cite: 66, 115]
# 4. 주요 산출물: 에폭별 기록(05_*_history.csv), 학습곡선(05_*_curves.png), 요약표(05_comparison.csv)[cite: 115]
# ==============================================================================

from pathlib import Path
import pandas as pd
import torch
from torch import nn

# CPU 연산 스레드 수를 1개로 고정하여 실행할 때마다 결과가 달라지는 것을 방지(재현성 확보)합니다.[cite: 115]
torch.set_num_threads(1)
base = Path(__file__).resolve().parent
from torch.utils.data import TensorDataset, DataLoader
import copy
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다.[cite: 115]
import matplotlib.pyplot as plt

# 결과물(CSV, PNG)을 저장할 outputs 폴더를 생성합니다.[cite: 115]
out = base / "outputs"
out.mkdir(exist_ok=True)
# 재현용 기본값 CPU. GPU 실습은 강사 확인 뒤 device 문자열만 cuda:0으로 바꿉니다.[cite: 115]
device = torch.device("cpu")
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()
# Dropout 확률 p=0.0과 p=0.3을 비교하세요.[cite: 115]
# 평가에서는 model.eval()과 no_grad를 모두 사용하고, best epoch는 valid loss로 찾습니다.[cite: 115]
# >>> A05
# TODO A05: 위 요구사항에 맞게 이 블록만 완성합니다.[cite: 115]
configs = [
    {'name': 'dropout0.0', 'lr': 0.01, 'dropout': 0.0},
    {'name': 'dropout0.3', 'lr': 0.01, 'dropout': 0.3}
]
# <<< A05
summary = []

# 정의한 두 가지 설정(dropout 0.0, dropout 0.3)을 순회하며 동일한 조건에서 실험합니다.[cite: 115]
for config in configs:
    # 가중치 초기화 난수를 42로 고정하여 두 모델이 완전히 똑같은 초기 가중치에서 출발하게 합니다.[cite: 24, 54, 115]
    torch.manual_seed(42)
    # config에 "width"가 따로 지정되지 않았으므로 기본값인 32가 사용됩니다.[cite: 115]
    width = config.get("width", 32)
    layers = [nn.Linear(2, width)]
    if config.get("bn", False):
        layers.append(nn.BatchNorm1d(width))
        
    # [핵심 개념 & 함수: nn.Dropout(p)]
    # - 역할: 학습(train) 중에만 중간 활성화 값(Activation)의 원소들을 확률 p(예: 0.3 = 30%)로 무작위로 0으로 만듭니다.[cite: 8, 59, 60]
    # - 이유: 모델이 특정 뉴런이나 특정 특징에만 과도하게 의존(동조화)하는 것을 막아 과적합을 방지합니다.[cite: 8]
    # - 스케일 보정: 학습 때 일부 뉴런이 꺼져 전체 합이 줄어드는 것을 보상하기 위해, 살아남은 값들을 1/(1-p)배 키워줍니다.[cite: 59]
    # - 위치: 일반적으로 선형 층(Linear) -> 활성화 함수(ReLU) 직후에 배치합니다.[cite: 8, 63]
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, width)])
    if config.get("bn", False):
        layers.append(nn.BatchNorm1d(width))
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, 2)])
    
    # 조립된 레이어 리스트를 언패킹(*layers)하여 순차 모델로 만들고 장치(device)로 보냅니다.[cite: 115]
    model = nn.Sequential(*layers).to(device)
    # shuffle용 Generator를 후보마다 같은 seed로 다시 만듭니다.[cite: 115]
    # (Dropout이 학습 중에 난수를 소모하더라도, 미니배치가 섞이는 순서는 두 실험에서 100% 같도록 분리)[cite: 54, 115]
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                        generator=torch.Generator().manual_seed(43), num_workers=0)
    if config.get("optimizer", "AdamW") == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                    momentum=config.get("momentum", 0.0), weight_decay=0.0)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
        
    history = []
    # 1 에폭부터 40 에폭까지 학습과 평가를 반복합니다.[cite: 115]
    for epoch in range(1, 40 + 1):
        # [핵심 함수 1: model.train()]
        # 모델을 '학습 모드'로 전환합니다. 이때 nn.Dropout 층이 활성화되어 매 순전파(forward)마다 
        # 새로운 무작위 마스크를 생성해 뉴런의 30%(p=0.3)를 임시로 끕니다.[cite: 61, 62, 67]
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()        # 이전 배치의 기울기 초기화[cite: 7, 46]
            loss = loss_fn(model(xb), yb) # Dropout이 켜진 상태에서 예측 및 손실 계산[cite: 7, 61]
            loss.backward()              # 역전파로 기울기 계산[cite: 7]
            optimizer.step()             # 가중치 갱신[cite: 7, 46]
            
        # 같은 epoch 말 모델을 eval 모드로 비교합니다. 학습 중 Dropout loss와 구분합니다.[cite: 9, 115]
        # [핵심 함수 2: model.eval()]
        # 모델을 '평가 모드'로 전환합니다. 평가할 때는 무작위성이 들어가면 안 되므로 
        # Dropout 층이 자동으로 비활성화(Identity 동작: 입력을 끄지 않고 100% 그대로 통과)됩니다.[cite: 8, 60, 61, 67]
        # 주의: model.eval()은 Dropout/BatchNorm의 동작만 바꿀 뿐 기울기 계산을 끄지 않으므로, 
        # 반드시 아래의 with torch.no_grad():와 세트로 함께 사용해야 합니다![cite: 14, 61, 62, 67]
        model.eval()
        with torch.no_grad():
            # 학습 데이터(X_train)도 공정한 비교를 위해 Dropout을 끈 상태(eval)에서 손실을 다시 측정합니다.[cite: 9, 115]
            train_loss = loss_fn(model(X_train.to(device)), y_train.to(device)).item()
            logits = model(X_valid)
            valid_loss = loss_fn(logits, y_valid).item()
            valid_acc = (logits.argmax(1) == y_valid).float().mean().item()
        history.append([epoch, train_loss, valid_loss, valid_acc])
        
    # 에폭별 기록을 DataFrame 표로 만들고 검증 손실(valid_loss)이 가장 낮은 최적의 시점(best epoch)을 찾습니다.[cite: 55, 115]
    table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss", "valid_acc"])
    best = table.loc[table["valid_loss"].idxmin()]
    name = config["name"]
    table.to_csv(out / f"05_{name}_history.csv", index=False)
    
    # 실험 설정값과 Best Epoch 시점의 성능, 마지막 40 에폭 시점의 손실을 하나의 딕셔너리로 묶어 요약 리스트에 추가합니다.[cite: 115]
    summary.append({**config, "best_epoch": int(best["epoch"]),
                    "best_valid_loss": float(best["valid_loss"]),
                    "valid_acc_at_best": float(best["valid_acc"]),
                    "last_train_loss_eval": train_loss, "last_valid_loss": valid_loss})
                    
    # 에폭별 Train/Valid 손실 곡선과 Best Epoch 지점을 그래프로 그려 PNG 파일로 저장합니다.[cite: 55, 89, 115]
    plt.figure(figsize=(8, 5))
    plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval)")
    plt.plot(table["epoch"], table["valid_loss"], label="valid")
    plt.axvline(best["epoch"], linestyle="--", label="best epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / f"05_{name}_curves.png", dpi=150)
    plt.close()
    print(name, "best epoch:", int(best["epoch"]), "best valid loss:", round(best["valid_loss"], 6))

# 두 실험(dropout0.0 vs dropout0.3)의 최종 요약 비교표를 CSV로 저장합니다.[cite: 115]
result = pd.DataFrame(summary)
result.to_csv(out / "05_comparison.csv", index=False)
print("생성: outputs/05_*.csv, *.png / test 미사용")

# ==============================================================================
# [실험 결과 요약 및 진단 보고]
# 1. Dropout 미적용(p=0.0): 학습 초반에 빠르게 수렴하지만, 에폭이 진행될수록 훈련 데이터에만 
#    과적합되어 후반부 valid_loss가 다시 치솟는 현상이 나타날 수 있음.[cite: 9, 49, 64]
# 2. Dropout 적용(p=0.3): 학습 시 일부 뉴런을 무작위로 끄면서 특정 특징에 대한 과도한 의존을 줄여, 
#    후반부 에폭에서도 valid_loss 상승(과적합)이 억제되고 일반화 성능이 안정적으로 유지됨.[cite: 8, 58, 64]
# 3. 필수 점검 사항: 검증/추론 시 model.eval()을 누락하면 평가 때마다 무작위로 뉴런이 꺼져 
#    실행할 때마다 예측 결과가 달라지므로 반드시 model.eval() + torch.no_grad()를 함께 사용할 것![cite: 61, 65, 92]
# ==============================================================================