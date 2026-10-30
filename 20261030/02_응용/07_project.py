# ==============================================================================
# [실습 보고서: 07_project.py - 종합 파이프라인 및 최적 모델 복원(Best Checkpointing)]
# 1. 실험 목적: SGD vs AdamW vs AdamW+Dropout(0.3) 세 가지 후보 설정을 비교하고, 
#               학습 중 검증 손실(valid loss)이 가장 낮았던 최적 에폭의 가중치를 안전하게 보관(Checkpointing) 후 복원 평가
# 2. 고정 조건: 데이터 분할, Seed(42/43), 모델 폭(width=32), Epochs(40)
# 3. 변경 조건: Optimizer 종류(SGD vs AdamW) 및 규제 적용 여부(Dropout 0.0 vs 0.3)
# 4. 주요 산출물: 에폭별 기록(07_*_history.csv), 클래스별 지표(07_*_class_metrics.csv), 예측 결과(07_*_predictions.csv)
# ==============================================================================

from pathlib import Path
import pandas as pd
import torch
from torch import nn
from tqdm import tqdm  # 1. 터미널 진행률 바를 위한 tqdm 라이브러리를 임포트합니다.

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
device = torch.device("cuda:0")
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()
configs = [{'name': 'sgd', 'optimizer': 'SGD', 'lr': 0.01}, {'name': 'adamw', 'lr': 0.01}, {'name': 'adamw_dropout', 'lr': 0.01, 'dropout': 0.3}]
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
    
    # 2. 여기서 현재 실험 모델의 이름표('sgd', 'adamw', 'adamw_dropout')가 먼저 정의됩니다!
    name = config["name"]
    
    # shuffle용 Generator를 후보마다 같은 seed로 다시 만듭니다.
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                        generator=torch.Generator().manual_seed(43), num_workers=0)
    if config.get("optimizer", "AdamW") == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                    momentum=config.get("momentum", 0.0), weight_decay=0.0)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
    history = []
    best_loss = float("inf")
    best_state = None
    best_epoch = 0
    
    # 3. name 변수가 정의된 안쪽이므로 tqdm(range(...), desc=f"[{name}] Training")이 정상 작동합니다!
    for epoch in tqdm(range(1, 40 + 1), desc=f"[{name}] Training"):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            # A07 완료: 역전파 및 가중치 갱신
            loss.backward()
            optimizer.step()
            
        # A08 완료: 에폭 종료 후 평가 모드 전환
        model.eval()
        with torch.no_grad():
            train_loss = loss_fn(model(X_train.to(device)), y_train.to(device)).item()
            logits = model(X_valid)
            valid_loss = loss_fn(logits, y_valid).item()
            valid_acc = (logits.argmax(1) == y_valid).float().mean().item()
            
            # A09 완료: 최적 loss·epoch와 독립된 state_dict 복사본 보관
            if valid_loss < best_loss:
                best_loss = valid_loss
                best_epoch = epoch
                best_state = copy.deepcopy(model.state_dict())
                
        history.append([epoch, train_loss, valid_loss, valid_acc])
        
    table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss", "valid_acc"])
    table.to_csv(out / f"07_{name}_history.csv", index=False)
    summary.append({**config, "best_epoch": best_epoch,
                    "best_valid_loss": float(best_loss),
                    "valid_acc_at_best": float(table.loc[table["epoch"] == best_epoch, "valid_acc"].values[0]),
                    "last_train_loss_eval": train_loss, "last_valid_loss": valid_loss})
                    
    # 제공 코드: 학습이 끝난 뒤 최적 상태로 복원하고 그 모델로 다시 평가합니다.
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        best_pred = model(X_valid).argmax(1).cpu()
        restored_loss = loss_fn(model(X_valid), y_valid).item()
    labels = y_valid.cpu()
    class_rows = []
    for label in (0, 1):
        # A10 완료: 클래스별 실제 표본 수·정답 수·Recall 기록
        mask = (labels == label)
        support = int(mask.sum().item())
        if support == 0:
            recall = None
            correct = 0
        else:
            correct = int((best_pred[mask] == labels[mask]).sum().item())
            recall = correct / support
        class_rows.append({"label": label, "support": support, "correct": correct, "recall": recall})
        
    pd.DataFrame(class_rows).to_csv(out / f"07_{name}_class_metrics.csv", index=False)
    pd.DataFrame({"id":valid["id"].tolist(),"actual":labels.tolist(),
                  "predicted":best_pred.tolist()}).to_csv(out / f"07_{name}_predictions.csv", index=False)
    summary[-1]["restored_valid_loss"] = restored_loss
    summary[-1]["restored_matches_best"] = abs(restored_loss-best_loss) < 1e-6
    
    plt.figure(figsize=(8, 5))
    plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval)")
    plt.plot(table["epoch"], table["valid_loss"], label="valid")
    plt.axvline(best_epoch, linestyle="--", label="best epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / f"07_{name}_curves.png", dpi=150)
    plt.close()
    print(name, "best epoch:", best_epoch, "best valid loss:", round(best_loss, 6))

result = pd.DataFrame(summary)
result.to_csv(out / "07_comparison.csv", index=False)
print("생성: outputs/07_*.csv, *.png / test 미사용")

# ==============================================================================
# [실험 결과 요약 및 종합 진단 보고]
# 1. 학습 파이프라인 완성: 미니배치 순전파 -> loss.backward() -> optimizer.step() 루프 확립
# 2. 베스트 모델 저장: copy.deepcopy(model.state_dict())를 통해 과적합 전 최적 에폭 가중치 복원
# 3. tqdm 시각화: 각 모델별(sgd, adamw, adamw_dropout) 학습 진행률 바(100%) 실시간 모니터링 적용
# ==============================================================================