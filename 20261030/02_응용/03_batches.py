from pathlib import Path
import pandas as pd
import torch
from torch import nn

# CPU 연산 스레드 수를 1개로 고정하여 일관된 연산 환경을 유지합니다.
torch.set_num_threads(1)
base = Path(__file__).resolve().parent
from torch.utils.data import TensorDataset, DataLoader
import copy
import matplotlib
matplotlib.use("Agg")  # GUI 창을 띄우지 않고 백그라운드에서 PNG 파일로 저장합니다.
import matplotlib.pyplot as plt

# 결과물을 저장할 outputs 디렉터리를 생성합니다.
out = base / "outputs"
out.mkdir(exist_ok=True)
# 재현용 기본값 CPU. GPU 실습은 강사 확인 뒤 device 문자열만 cuda:0으로 바꿉니다.
device = torch.device("cpu") # cuda:0(GPU 실습용)

# 데이터셋 CSV 파일을 불러와 학습용(train)과 검증용(valid)으로 분리합니다.
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]

# 학습 및 검증 데이터를 PyTorch 텐서(Tensor)로 변환하고, 검증 데이터는 지정된 장치(device)로 보냅니다.
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)

# 분류 모델을 위한 손실 함수(CrossEntropyLoss)를 선언합니다.
loss_fn = nn.CrossEntropyLoss()

# batch_size 후보를 [8, 32]로 두세요. 총 train 행은 240건입니다.
# drop_last=False이므로 32인 경우 마지막 배치는 16건입니다.
# >>> A03
# TODO A03: 위 요구사항에 맞게 이 블록만 완성합니다.
batch_sizes = [8, 32]
# <<< A03

rows = []
# 각 배치 사이즈별로 데이터를 나누어 DataLoader의 동작을 확인하고 기록합니다.
for size in batch_sizes:
    # TensorDataset으로 묶은 학습 데이터를 DataLoader에 전달하여 미니배치 단위로 로드할 준비를 합니다. (순서는 섞지 않음)
    loader = DataLoader(TensorDataset(X_train, y_train), batch_size=size, shuffle=False)
    
    # 각 배치의 데이터(y) 개수 목록을 추출합니다.
    counts = [len(yb) for xb, yb in loader]
    
    # [배치 사이즈, 총 Iteration(배치 개수), 마지막 배치 샘플 수, 총 처리된 샘플 수]를 리스트에 담습니다.
    rows.append([size, len(counts), counts[-1], sum(counts)])
    print("batch:", size, "iterations:", len(counts), "마지막:", counts[-1], "처리 수:", sum(counts))

# 실험 결과 통계를 DataFrame으로 변환한 뒤 outputs/03_batches.csv 파일로 저장합니다.
pd.DataFrame(rows, columns=["batch_size", "iterations", "last_batch", "samples"]).to_csv(
    out / "03_batches.csv", index=False)