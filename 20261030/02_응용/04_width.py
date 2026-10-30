# ==============================================================================
# [실습 보고서: 04_width.py - 모델 폭(Width)에 따른 학습곡선 및 과적합 진단]
# 1. 실험 목적: 은닉층 뉴런 수(width: 8 vs 64)가 모델의 표현력(Capacity)과 
#               과적합(Overfitting)에 미치는 영향을 학습곡선(Loss Curve)으로 비교[cite: 49, 56]
# 2. 고정 조건: 데이터 분할(Split), Seed(42/43), Optimizer(AdamW), lr(0.01), Epochs(40)[cite: 24, 114]
# 3. 변경 조건: 모델 은닉층의 폭 (width = 8 vs width = 64)[cite: 56, 114]
# 4. 주요 산출물: 에폭별 기록(04_*_history.csv), 학습곡선(04_*_curves.png), 요약표(04_comparison.csv)[cite: 114]
# ==============================================================================

from pathlib import Path
import pandas as pd
import torch
from torch import nn

# CPU 연산 스레드 수를 1개로 제한하여 실행할 때마다 결과가 달라지는 것을 방지(재현성 확보)합니다.[cite: 114]
torch.set_num_threads(1)
base = Path(__file__).resolve().parent
from torch.utils.data import TensorDataset, DataLoader
import copy
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다. (서버나 배치 작업 시 필수 설정)[cite: 114]
import matplotlib.pyplot as plt

# 결과 파일들을 저장할 outputs 폴더를 생성합니다. (이미 폴더가 있어도 에러가 나지 않게 exist_ok=True 설정)[cite: 114]
out = base / "outputs"
out.mkdir(exist_ok=True)
# 재현용 기본값 CPU. GPU 실습은 강사 확인 뒤 device 문자열만 cuda:0으로 바꿉니다.[cite: 114]
device = torch.device("cpu")
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()
# width 8과 64만 비교하세요. lr=0.01이고 각 40 epochs입니다.[cite: 114]
# 서로 다른 폭의 모델은 파라미터 모양이 달라 동일 가중치일 수 없으며, 같은 초기화 seed를 사용합니다.[cite: 114]
# >>> A04
# TODO A04: 위 요구사항에 맞게 이 블록만 완성합니다.[cite: 114]
configs = [
    {'name': 'width8', 'lr': 0.01, 'width': 8},
    {'name': 'width64', 'lr': 0.01, 'width': 64}
]
# <<< A04
summary = []

# 정의해 둔 실험 설정(width8, width64)을 하나씩 꺼내어 동일한 구조로 반복 실험합니다.[cite: 114]
for config in configs:
    # 가중치 초기화 난수를 42로 고정합니다.[cite: 54, 114]
    torch.manual_seed(42)
    
    # [새 문법: dict.get("키", 기본값)] 
    # config 딕셔너리에서 "width" 값을 가져오고, 만약 키가 없으면 기본값 32를 반환합니다.[cite: 114]
    width = config.get("width", 32)
    
    # [동적 모델 층(Layer) 조립]
    # 리스트에 층을 하나씩 담아서 나중에 nn.Sequential로 한 번에 묶어줍니다.
    # 첫 번째 층: 입력 특성 2개(x1, x2)를 받아서 은닉층 뉴런 수(width: 8 또는 64)로 확장합니다.[cite: 114]
    layers = [nn.Linear(2, width)]
    if config.get("bn", False):
        # 설정에 BatchNorm(bn)이 켜져 있을 때만 배치 정규화 층을 끼워 넣습니다.[cite: 71, 114]
        layers.append(nn.BatchNorm1d(width))
    # [새 함수: list.extend([...])] 리스트 끝에 여러 개의 층(활성화 함수 ReLU -> Dropout -> 두 번째 은닉층)을 한 번에 이어 붙입니다.[cite: 8, 114]
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, width)])
    if config.get("bn", False):
        layers.append(nn.BatchNorm1d(width))
    # 마지막 출력층: 은닉층 뉴런 수(width)를 받아 클래스 개수인 2개(0 또는 1의 점수)로 출력합니다.[cite: 63, 114]
    layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, 2)])
    
    # [새 문법: *layers (리스트 언패킹)]
    # 리스트 대괄호 []를 벗겨내고 안의 레이어 객체들을 낱개로 풀어서 nn.Sequential()에 전달한 뒤, 장치(device)로 이동시킵니다.[cite: 114]
    model = nn.Sequential(*layers).to(device)
    
    # shuffle용 Generator를 후보마다 같은 seed로 다시 만듭니다.[cite: 54, 114]
    # [새 개념: torch.Generator().manual_seed(43)]
    # 모델 파라미터 개수가 다르면 초기화 과정에서 난수를 소모하는 횟수가 달라집니다.
    # 따라서 DataLoader가 배치를 섞는(shuffle) 순서가 영향받지 않도록 전용 난수 생성기(Generator)를 따로 만들어 순서를 100% 동일하게 고정합니다.[cite: 54, 114]
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                        generator=torch.Generator().manual_seed(43), num_workers=0)
    
    # Optimizer 선택: 설정에 따라 SGD 또는 AdamW를 생성합니다. (이번 실습은 기본값인 AdamW가 선택됨)[cite: 25, 114]
    if config.get("optimizer", "AdamW") == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                    momentum=config.get("momentum", 0.0), weight_decay=0.0)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
        
    history = []
    # 1 에폭부터 40 에폭까지 학습 및 평가를 반복합니다.[cite: 114]
    for epoch in range(1, 40 + 1):
        # 1. 미니배치 단위로 가중치를 갱신하는 학습(Train) 단계[cite: 6, 7]
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()        # 이전 배치의 기울기 초기화[cite: 7, 46]
            loss = loss_fn(model(xb), yb) # 순전파 및 오차(Loss) 계산[cite: 7]
            loss.backward()              # 역전파로 기울기(Gradient) 계산[cite: 7]
            optimizer.step()             # 가중치(Parameter) 한 스텝 갱신[cite: 7, 46]
            
        # 같은 epoch 말 모델을 eval 모드로 비교합니다. 학습 중 Dropout loss와 구분합니다.[cite: 9, 17, 114]
        # 2. 1 에폭 학습이 끝난 시점의 모델을 공정하게 평가(Eval)하는 단계[cite: 6, 9]
        model.eval()
        with torch.no_grad(): # 평가 시에는 기울기 계산을 꺼서 메모리와 연산 속도를 아낍니다.[cite: 14, 61]
            # 학습 데이터 전체에 대한 평가 모드 손실(train_loss_eval)을 측정합니다.[cite: 9, 114]
            train_loss = loss_fn(model(X_train.to(device)), y_train.to(device)).item()
            # 검증 데이터(X_valid)를 모델에 통과시켜 클래스별 예측 점수(logits)를 얻습니다.[cite: 114]
            logits = model(X_valid)
            valid_loss = loss_fn(logits, y_valid).item()
            
            # [새 함수: logits.argmax(1)]
            # logits의 모양은 (데이터 수, 클래스 2개)입니다. 차원 1(가로 방향)에서 가장 점수가 높은 인덱스를 뽑아 예측 라벨(0 또는 1)을 만듭니다.
            # 정답(y_valid)과 비교하여 맞으면 True(1.0), 틀리면 False(0.0)로 바꾼 뒤 평균(.mean())을 내어 정확도(Accuracy)를 계산합니다.[cite: 114]
            valid_acc = (logits.argmax(1) == y_valid).float().mean().item()
        history.append([epoch, train_loss, valid_loss, valid_acc])
        
    # 에폭별 기록을 표(DataFrame)로 변환합니다.[cite: 55, 114]
    table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss", "valid_acc"])
    
    # [새 함수: idxmax() / idxmin()]
    # table["valid_loss"].idxmin()은 검증 손실(valid_loss)이 가장 낮았던(가장 성능이 좋았던) 행의 인덱스 번호를 찾아줍니다.
    # table.loc[...]를 통해 그 최적 에폭(best epoch)의 전체 기록(epoch, loss, acc)을 뽑아냅니다.[cite: 12, 55, 114]
    best = table.loc[table["valid_loss"].idxmin()]
    name = config["name"]
    table.to_csv(out / f"04_{name}_history.csv", index=False)
    
    # [새 문법: {**config, ...} (딕셔너리 언패킹 병합)]
    # 기존 config 딕셔너리의 내용('name', 'lr', 'width')을 그대로 펼쳐 넣고, 뒤에 best 성능 지표들을 추가해 새로운 딕셔너리로 만듭니다.[cite: 114]
    summary.append({**config, "best_epoch": int(best["epoch"]),
                    "best_valid_loss": float(best["valid_loss"]),
                    "valid_acc_at_best": float(best["valid_acc"]),
                    "last_train_loss_eval": train_loss, "last_valid_loss": valid_loss})
                    
    # [학습곡선(Learning Curve) 시각화 및 이미지 파일 저장][cite: 55, 89, 114]
    plt.figure(figsize=(8, 5)) # 가로 8인치, 세로 5인치 크기의 도화지 생성[cite: 114]
    plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval)") # 에폭별 Train Loss 선 그래프[cite: 114]
    plt.plot(table["epoch"], table["valid_loss"], label="valid")             # 에폭별 Valid Loss 선 그래프[cite: 114]
    # [새 함수: plt.axvline()] 검증 손실이 가장 낮았던 Best Epoch 위치에 세로 점선(--)을 그어 한눈에 표시합니다.[cite: 89, 114]
    plt.axvline(best["epoch"], linestyle="--", label="best epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()       # 그래프 범례(label) 표시[cite: 114]
    plt.tight_layout() # 여백을 자동으로 깔끔하게 정리[cite: 114]
    plt.savefig(out / f"04_{name}_curves.png", dpi=150) # 해상도 150 dpi로 PNG 이미지 저장[cite: 114]
    plt.close()        # 메모리가 쌓이지 않도록 현재 그린 도화지를 닫아줍니다.[cite: 114]
    print(name, "best epoch:", int(best["epoch"]), "best valid loss:", round(best["valid_loss"], 6))

# 전체 실험 요약 리스트를 DataFrame으로 만들어 최종 비교 CSV로 저장합니다.[cite: 12, 114]
result = pd.DataFrame(summary)
result.to_csv(out / "04_comparison.csv", index=False)
print("생성: outputs/04_*.csv, *.png / test 미사용")

# ==============================================================================
# [실험 결과 요약 및 진단 보고]
# 1. 모델 폭 비교: width=8(작은 용량)보다 width=64(큰 용량) 모델이 학습 데이터(train loss)를 
#                  훨씬 더 빠르게 줄이며 복잡한 경계를 학습함.[cite: 49, 50, 56]
# 2. 과적합(Overfitting) 징후: 모델 폭이 커질수록(width=64) 특정 에폭(Best Epoch) 이후 
#    train loss는 계속 감소하지만 valid loss는 정체되거나 다시 상승하는 격차가 발생할 수 있음.[cite: 9, 49, 51]
# 3. 실무 적용 포인트: 마지막 40번째 에폭(last epoch)의 모델이 항상 최선이 아니므로, 
#    검증 손실이 최저점인 'best_epoch'를 기준으로 모델을 선택하거나 규제(Dropout 등)를 적용해야 함.[cite: 10, 51, 55]
# ==============================================================================