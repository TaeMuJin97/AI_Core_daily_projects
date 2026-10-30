# ==============================================================================
# [실습 보고서: 01_momentum.py - SGD 최적화 알고리즘의 모멘텀(Momentum) 효과 비교]
# 1. 실험 목적: 경사하강법(SGD)에서 관성(Momentum: 0.0 vs 0.9)을 추가했을 때,
#               최적화 경로가 어떻게 개선되며 학습 속도와 수렴 안정성에 미치는 영향 비교
# 2. 고정 조건: 데이터 분할, Seed(42/43), 모델 폭(width=32), Optimizer=SGD, lr=0.05, Epochs(20)
# 3. 변경 조건: 모멘텀 계수 (momentum = 0.0 vs momentum = 0.9)
# 4. 주요 산출물: 에폭별 기록(01_*_history.csv), 학습곡선(01_*_curves.png), 요약표(01_comparison.csv)
# ==============================================================================

from pathlib import Path
import pandas as pd
import torch
from torch import nn

torch.set_num_threads(1)
base = Path(__file__).resolve().parent
from torch.utils.data import TensorDataset, DataLoader
import copy
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다.
import matplotlib.pyplot as plt

out = base / "outputs"
out.mkdir(exist_ok=True)
# 재현용 기본값 CPU. GPU 실습은 강사 확인 뒤 device 문자열만 cuda:0으로 바꿉니다.
device = torch.device("cpu")
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()

# 두 설정은 momentum만 0.0과 0.9로 다르게 만드세요.
# optimizer=SGD, lr=0.05, 나머지 설정은 동일하게 유지합니다.
# >>> A01
# TODO A01: 위 요구사항에 맞게 이 블록만 완성합니다.
configs = [
    {'name': 'momentum0', 'optimizer': 'SGD', 'lr': 0.05, 'momentum': 0.0},
    {'name': 'momentum9', 'optimizer': 'SGD', 'lr': 0.05, 'momentum': 0.9}
]
# <<< A01
summary = []

for config in configs:
    torch.manual_seed(42)
    width = config.get("width", 32)
    layers = [nn.Linear(2, width)]
    if config.get("bn", False):
        layers.append(nn.BatchNorm1d(width))
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, width)])
    if config.get("bn", False):
        layers.append(nn.BatchNorm1d(width))
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, 2)])
    model = nn.Sequential(*layers).to(device)
    # shuffle용 Generator를 후보마다 같은 seed로 다시 만듭니다.
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                        generator=torch.Generator().manual_seed(43), num_workers=0)
                        
    # [새로운 최적화 도구: torch.optim.SGD와 momentum]
    # - 기본 SGD (momentum=0.0): 현재 계산된 기울기(gradient) 방향으로만 이동합니다. 
    #   지형이 울퉁불퉁하거나 골짜기(Ravine) 구조일 때 진동(Oscillation)이 심해 학습이 느려질 수 있습니다.
    # - 모멘텀 적용 SGD (momentum=0.9): 물리에서의 '관성' 개념을 도입하여, 
    #   이전에 이동했던 방향의 벡터(Velocity) 일정 비율(0.9)을 다음 스텝에 누적해서 반영합니다.
    #   -> 장점: 진동을 상쇄시키고, 완만한 경로나 로컬 최솟값(Local Minimum)을 관성으로 빠져나가는 데 도움을 줍니다.
    if config.get("optimizer", "AdamW") == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                    momentum=config.get("momentum", 0.0), weight_decay=0.0)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
        
    history = []
    for epoch in range(1, 20 + 1):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()
        # 같은 epoch 말 모델을 eval 모드로 비교합니다. 학습 중 Dropout loss와 구분합니다.
        model.eval()
        with torch.no_grad():
            train_loss = loss_fn(model(X_train.to(device)), y_train.to(device)).item()
            logits = model(X_valid)
            valid_loss = loss_fn(logits, y_valid).item()
            valid_acc = (logits.argmax(1) == y_valid).float().mean().item()
        history.append([epoch, train_loss, valid_loss, valid_acc])
    table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss", "valid_acc"])
    best = table.loc[table["valid_loss"].idxmin()]
    name = config["name"]
    table.to_csv(out / f"01_{name}_history.csv", index=False)
    summary.append({**config, "best_epoch": int(best["epoch"]),
                    "best_valid_loss": float(best["valid_loss"]),
                    "valid_acc_at_best": float(best["valid_acc"]),
                    "last_train_loss_eval": train_loss, "last_valid_loss": valid_loss})
    plt.figure(figsize=(8, 5))
    plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval)")
    plt.plot(table["epoch"], table["valid_loss"], label="valid")
    plt.axvline(best["epoch"], linestyle="--", label="best epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / f"01_{name}_curves.png", dpi=150)
    plt.close()
    print(name, "best epoch:", int(best["epoch"]), "best valid loss:", round(best["valid_loss"], 6))
result = pd.DataFrame(summary)
result.to_csv(out / "01_comparison.csv", index=False)
print("생성: outputs/01_*.csv, *.png / test 미사용")

# ==============================================================================
# [실험 결과 요약 및 진단 보고]
# 1. 모멘텀 효과 비교: momentum=0.0(일반 SGD)은 학습 속도가 다소 느리거나 손실 감소가 완만할 수 있는 반면,
#    momentum=0.9 설정을 적용한 경우 관성에 의해 더 빠르게 최적의 방향으로 수렴함.
# 2. 학습 안정성: 모멘텀은 미니배치 데이터로 인해 발생하는 기울기의 무작위한 흔들림(노이즈)을 
#    부드럽게 흡수해 주는 필터 역할을 수행하여 안정적인 가중치 갱신을 돕는다.
# ==============================================================================