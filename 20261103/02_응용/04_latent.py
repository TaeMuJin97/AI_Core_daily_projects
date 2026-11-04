"""
==============================================================================
[실습 보고서: 04_latent.py - Autoencoder 병목(Latent) 차원 크기에 따른 압축률 및 복원 오차 비교]
1. 실험 목적: 8차원 시계열 구간 데이터를 입력받아 Latent 차원을 1, 2, 4로 변화시키며
              정보 보존 비율(retained_ratio)과 재구성 오차(valid_mse) 간의 트레이드오프 관계를 확인함.
2. 고정 조건: 입력 차원(8), 활성화 함수(Tanh), 손실 함수(MSELoss, 입력=정답), Optimizer(Adam, lr=0.02), Epochs(40)
3. 변경 조건: 병목 구간 크기 latent_size = [1, 2, 4] (보존 비율 12.5%, 25.0%, 50.0%)
4. 주요 산출물: outputs/latent_comparison.csv (Latent 크기별 압축 비율, 파라미터 수, 최적 에폭, 복원 MSE)
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

df = pd.read_csv(ROOT / "data" / "series.csv")
train = torch.tensor(df.loc[df["split"] == "train", "value"].values, dtype=torch.float32)
valid = torch.tensor(df.loc[df["split"] == "valid", "value"].values, dtype=torch.float32)

# [핵심 포인트 1: unfold 후 .contiguous() 호출]
# unfold는 메모리를 새로 할당하지 않고 원본 텐서의 스트라이드(보폭)만 바꾼 View를 반환합니다.
# 이후 Linear 연산 등에서 메모리 연속성 문제가 생기지 않도록 .contiguous()로 메모리를 일렬로 정렬해 줍니다.
x = train.unfold(0, 8, 1).contiguous()
v = valid.unfold(0, 8, 1).contiguous()
rows = []

for latent_size in [1, 2, 4]:
    torch.manual_seed(42)
    # TODO A04: 후보 latent_size=1·2·4를 실제 Encoder·Decoder 크기에 적용한다.
    # BEGIN A04
    # [핵심 포인트 2: 대칭형 Encoder-Decoder 병목(Bottleneck) 설계]
    # Encoder: 8차원 입력을 latent_size 차원으로 압축 후 Tanh 비선형 변환 적용
    # Decoder: 압축된 latent_size 표현을 다시 원래의 8차원으로 복원
    model = nn.Sequential(
        nn.Linear(8, latent_size),
        nn.Tanh(),
        nn.Linear(latent_size, 8),
    )
    # END A04
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    best = float("inf")
    
    for epoch in range(1, 41):
        optimizer.zero_grad()
        # [핵심 포인트 3: 자기지도 재구성 학습 (Self-Supervised Reconstruction)]
        # 별도의 정답 라벨 y 없이 원본 입력 x 자체를 정답(Target)으로 삼아 복원 오차를 최소화합니다.
        loss = nn.MSELoss()(model(x), x)
        loss.backward()
        optimizer.step()
        
        with torch.inference_mode():
            score = nn.MSELoss()(model(v), v).item()
        if score < best:
            best = score
            best_epoch = epoch
            
    rows.append({
        "latent": latent_size,
        "retained_ratio": latent_size / 8,
        "params": sum(p.numel() for p in model.parameters()),
        "best_epoch": best_epoch,
        "valid_mse": best,
    })

table = pd.DataFrame(rows)
table.to_csv(OUT / "latent_comparison.csv", index=False)
print(table.round(6).to_string(index=False))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Latent 차원 크기에 따른 복원 성능 변화:
   - latent=1 (압축률 12.5%): 8개 시점의 패턴을 단 1개의 숫자로 요약해야 하므로 정보 손실이 커서 valid_mse가 가장 높음(Underfitting 경향).
   - latent=2 -> 4 (압축률 25% -> 50%): 병목 차원이 넓어질수록 더 많은 파형 정보를 담을 수 있어 valid_mse가 단계적으로 감소함.
2. 이상 탐지(Anomaly Detection) 관점의 설계 시사점:
   - 무조건 복원 오차가 낮다고 좋은 것이 아니라, 정상 패턴만 잘 복원하고 비정상 패턴은 복원하지 못하도록 적절한 병목 크기(예: latent=2)를 선택하는 것이 중요함.
==============================================================================
"""