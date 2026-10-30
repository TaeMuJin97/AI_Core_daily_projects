# ==============================================================================
# [실습 보고서: 06_batchnorm.py - 배치 정규화(BatchNorm1d) 적용 및 Train/Eval 통계 비교]
# 1. 실험 목적: 은닉층의 출력 분포를 미니배치 단위로 정규화하는 BatchNorm1d가 
#               학습 안정성과 수렴 속도에 미치는 영향을 확인하고, 학습/평가 모드의 출력 차이를 진단함
# 2. 고정 조건: 데이터 분할, Seed(42/43), 모델 폭(width=32), Optimizer(AdamW), lr(0.01), Epochs(40)
# 3. 변경 조건: BatchNorm1d 적용 여부 (bn = False vs bn = True)
# 4. 주요 산출물: 에폭별 기록(06_*_history.csv), 학습곡선(06_*_curves.png), 요약표(06_comparison.csv)
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
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()
# bn=False와 bn=True만 다른 두 설정을 구성하세요.
# batch_size=32는 동일하고 마지막 16건도 학습합니다. BatchNorm을 사용하는 train batch는 2건 이상이어야 합니다.
# >>> A06
# TODO A06: 위 요구사항에 맞게 이 블록만 완성합니다.
configs = [
    {'name': 'baseline', 'lr': 0.01, 'bn': False},
    {'name': 'batchnorm', 'lr': 0.01, 'bn': True}
]
# <<< A06
summary = []

for config in configs:
    torch.manual_seed(42)
    width = config.get("width", 32)
    layers = [nn.Linear(2, width)]
    
    # [핵심 개념 & 함수: nn.BatchNorm1d(num_features)]
    # - 역할: 각 층을 통과한 활성화 값들이 너무 커지거나 작아지지 않도록(내부 공변량 변화 완화), 
    #         미니배치 단위로 평균 0, 분산 1이 되도록 정규화한 뒤 학습 가능한 스케일(gamma)과 이동(beta)을 적용합니다.
    # - 배치 위치: 일반적으로 선형 층(nn.Linear) 직후, 활성화 함수(nn.ReLU) 직전에 배치합니다. (Linear -> BatchNorm1d -> ReLU -> Dropout)
    # - 주의사항: 배치 내의 '분산'을 계산해야 하므로, 학습(train) 시 미니배치 크기가 1이면 에러가 발생합니다(최소 2건 이상 필수).
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
    if config.get("optimizer", "AdamW") == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                    momentum=config.get("momentum", 0.0), weight_decay=0.0)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
    history = []
    for epoch in range(1, 40 + 1):
        # [BatchNorm의 model.train() 동작]
        # 1) 현재 들어온 미니배치(32건 또는 마지막 16건)의 평균과 분산을 실시간으로 계산하여 정규화합니다.
        # 2) 동시에 평가(eval) 때 사용할 전체 데이터의 이동평균(running_mean)과 이동분산(running_var)을 내부적으로 조금씩 업데이트합니다.
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()
        # 같은 epoch 말 모델을 eval 모드로 비교합니다. 학습 중 Dropout loss와 구분합니다.
        # [BatchNorm의 model.eval() 동작]
        # 평가 시에는 배치 크기에 따라 예측값이 흔들리면 안 되므로(1건씩 추론할 수도 있음), 
        # 현재 배치의 통계를 쓰지 않고 학습 중에 누적해 둔 고정 통계(running_mean, running_var)를 사용해 정규화합니다.
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
    table.to_csv(out / f"06_{name}_history.csv", index=False)
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
    plt.savefig(out / f"06_{name}_curves.png", dpi=150)
    plt.close()
    print(name, "best epoch:", int(best["epoch"]), "best valid loss:", round(best["valid_loss"], 6))
result = pd.DataFrame(summary)
result.to_csv(out / "06_comparison.csv", index=False)
print("생성: outputs/06_*.csv, *.png / test 미사용")

# 마지막 BN 모델을 복사해 진단합니다. 원래 학습 결과/저장 결과는 바꾸지 않습니다.
# [새 기능 & 진단 로직: copy.deepcopy 및 train/eval 출력 비교]
# - copy.deepcopy(model): 원본 모델과 메모리를 전혀 공유하지 않는 완전한 복제본(probe)을 만듭니다.
#   (왜 복제하나요? BatchNorm은 train() 모드로 순전파를 한 번만 실행해도 내부의 running_mean/var 통계가 변형되므로 원본 모델을 보호하기 위함입니다.)
probe = copy.deepcopy(model)
xb = X_train[:32].to(device)

# 1) 학습 모드(train)에서의 출력: xb(32건) 자체의 평균/분산으로 정규화한 예측값
probe.train()
with torch.no_grad():
    train_output = probe(xb)

# 2) 평가 모드(eval)에서의 출력: 학습 동안 누적된 전체 running_mean/var로 정규화한 예측값
probe.eval()
with torch.no_grad():
    eval_output = probe(xb)

# [새 텐서 연산: .abs().max().item()]
# 똑같은 입력(xb)과 똑같은 가중치를 넣었음에도, 사용하는 정규화 통계(현재 배치 통계 vs 누적 이동평균)가 달라서 발생하는 
# 두 출력 간의 차이의 절댓값(.abs()) 중 최댓값(.max())을 스칼라(.item())로 뽑아 확인합니다.
print("진단용 복사 모델 train/eval 최대 차이:", round((train_output - eval_output).abs().max().item(), 6))

# ==============================================================================
# [실험 결과 요약 및 진단 보고]
# 1. BatchNorm1d의 효과: 은닉층의 입력 분포를 일정하게 맞춰주어 기울기 소실/폭주를 완화하고, 
#    baseline(bn=False) 대비 초기 수렴 속도와 학습 안정성을 높여줌.
# 2. Train vs Eval 출력 차이의 의미: 진단 코드에서 'train_output'과 'eval_output'의 차이가 0이 아닌 양수로 나오는 이유는,
#    BatchNorm이 train 모드에서는 '현재 미니배치의 평균/분산'을 쓰고, eval 모드에서는 '누적된 이동평균(running stats)'을 쓰기 때문임.
# 3. 실무 주의사항: 
#    - train 모드에서 순전파를 실행하면 loss.backward()를 안 해도 BatchNorm의 running 통계가 갱신되므로 실험 시 원본 모델 오염에 주의할 것.
#    - 마지막 미니배치 크기가 1이 될 가능성이 있는 데이터셋에서는 DataLoader에 drop_last=True 설정을 고려해야 함.
# ==============================================================================