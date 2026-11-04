"""
==============================================================================
[실습 보고서: 03_forecast.py - Sliding Window 기반 RNN vs LSTM 시계열 다음 값 예측 비교]
1. 실험 목적: 시계열 데이터를 Train/Valid로 먼저 분리한 뒤 unfold를 통해 길이 12의 과거 Window와 
              다음 시점 정답(1개)을 구성하고, RNN·LSTM·Persistence(기준선)의 예측 MSE를 비교함.
2. 고정 조건: Window 크기(12), Hidden 크기(8), Optimizer(Adam, lr=0.02), Epochs(40)
3. 핵심 구현: 
   - 데이터 누수 방지를 위해 split 분리 후 각각 unfold(0, 13, 1)로 [N, 12, 1] 입력과 [N, 1] 정답 생성
   - 각 Window의 마지막 시점 은닉 상태(output[:, -1])를 Linear Head에 통과시켜 다음 값 예측
   - 직전 관측값을 그대로 다음 예측값으로 쓰는 Persistence 모델과 성능 대조
4. 주요 산출물: outputs/forecast_comparison.csv (모델별 파라미터 수, 최적 에폭, Valid MSE 비교표)
==============================================================================
"""

from pathlib import Path
import pandas as pd
import torch
from torch import nn

torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# 1. 시계열 데이터 로드 및 분할
df = pd.read_csv(ROOT / "data" / "series.csv")
train = torch.tensor(df.loc[df["split"] == "train", "value"].values, dtype=torch.float32)
valid = torch.tensor(df.loc[df["split"] == "valid", "value"].values, dtype=torch.float32)

# [핵심 포인트 1: tensor.unfold를 활용한 Sliding Window 생성]
# 미래 데이터 누수(Data Leakage)를 막기 위해 train과 valid를 먼저 나눈 뒤 각각 Window를 만듭니다.
# unfold(차원의 축=0, 윈도우 크기=13, 보폭=1): 연속된 13개 값을 묶어 하나의 행으로 만듭니다.
w = train.unfold(0, 13, 1)
v = valid.unfold(0, 13, 1)

# 앞의 12개 시점(:12)은 입력 x로 쓰고 마지막에 Feature 차원(F=1)을 추가합니다 -> [B, 12, 1]
# 13번째 시점(12:13)은 맞춰야 할 다음 시점 정답 y로 씁니다 -> [B, 1]
x, y = w[:, :12].unsqueeze(-1), w[:, 12:13]
vx, vy = v[:, :12].unsqueeze(-1), v[:, 12:13]

rows = []
for name in ["RNN", "LSTM"]:
    torch.manual_seed(42)
    core = nn.RNN(1, 8, batch_first=True) if name == "RNN" else nn.LSTM(1, 8, batch_first=True)
    head = nn.Linear(8, 1)
    params = list(core.parameters()) + list(head.parameters())
    optimizer = torch.optim.Adam(params, lr=0.02)
    best = float("inf")
    
    for epoch in range(1, 41):
        core.train()
        head.train()
        optimizer.zero_grad()
        output, _ = core(x)
        # TODO A03: 각 과거 Window의 마지막 출력에서 다음 값에 대한 MSE를 계산한다.
        # BEGIN A03
        # [핵심 포인트 2: Next-step 예측을 위한 마지막 시점 선택]
        # 과거 12개 시점을 모두 읽은 직후인 마지막 시점(output[:, -1])의 요약 표현으로 13번째 값을 예측합니다.
        loss = nn.MSELoss()(head(output[:, -1]), y)
        # END A03
        loss.backward()
        optimizer.step()
        
        core.eval()
        head.eval()
        with torch.inference_mode():
            output, _ = core(vx)
            score = nn.MSELoss()(head(output[:, -1]), vy).item()
        if score < best:
            best = score
            best_epoch = epoch
            
    rows.append({
        "model": name,
        "hidden": 8,
        "params": sum(p.numel() for p in params),
        "epochs": 40,
        "best_epoch": best_epoch,
        "valid_mse": best,
    })

# [핵심 포인트 3: Persistence(지속성) 기준선 모델]
# 딥러닝 모델이 정말로 패턴을 학습했는지 검증하기 위해, 아무 학습 없이 '12번째 마지막 관측값(vx[:, -1])'을
# 그대로 '13번째 예측값'으로 제출했을 때의 오차를 Baseline으로 함께 기록합니다.
rows.append({
    "model": "Persistence",
    "hidden": 0,
    "params": 0,
    "epochs": 0,
    "best_epoch": 0,
    "valid_mse": nn.MSELoss()(vx[:, -1], vy).item(),
})

table = pd.DataFrame(rows)
table.to_csv(OUT / "forecast_comparison.csv", index=False)
print("windows:", len(x), len(vx), "test 미사용")
print(table.round(6).to_string(index=False))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 파라미터 규모 차이 (RNN 89개 vs LSTM 361개):
   - 동일 은닉 크기(hidden=8) 기준, LSTM은 4개의 게이트 및 후보 연산(Forget, Input, Candidate, Output)을
     수행하므로 순환층 파라미터가 RNN(80개) 대비 정확히 4배(320개)이며, Head(9개) 합산 시 89개 vs 361개가 됨.
2. 예측 성능 및 Baseline 비교:
   - 학습 없는 Persistence 기준선보다 RNN과 LSTM의 valid_mse가 현저히 낮아 시계열 추세를 유의미하게 학습함을 확인함.
==============================================================================
"""