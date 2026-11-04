"""
==============================================================================
[실습 보고서: 06_transformer.py - Transformer Encoder 기반 가변 길이 Sequence 분류]
1. 실험 목적: 가변 길이 시퀀스(JSON)를 패딩하여 배치로 묶고, Linear Projection과 학습 가능한
              Position Embedding을 결합한 뒤, Padding Mask와 Masked Mean Pooling을 적용해 시퀀스를 분류함.
2. 고정 조건: 최대 길이(max_len=12), 모델 차원(d_model=8), Head 수(2), FFN 차원(16), Epochs(30)
3. 핵심 구현: 
   - 값 투영(projection: 3->8)과 위치 임베딩(position: 12->8)을 더하여 순서 정보 주입
   - TransformerEncoder 호출 시 src_key_padding_mask=mt 전달로 패딩 Key 참조 차단
   - 출력 시퀀스에서 패딩 Query를 제외하고 실제 길이(lt, lv)로 나누는 Masked Mean Pooling 수행
4. 주요 산출물: outputs/transformer_predictions.csv (검증 샘플 ID, 실제 라벨, 예측 라벨 비교표)
==============================================================================
"""

import json
from pathlib import Path
import pandas as pd
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence

torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# 1. JSON 시퀀스 데이터 로드 및 Train / Valid 분할
items = json.loads((ROOT / "data" / "sequences.json").read_text(encoding="utf-8"))
tr = [r for r in items if r["split"] == "train"]
va = [r for r in items if r["split"] == "valid"]
max_len = 12

# 2. 가변 길이 시퀀스 패딩 및 불리언 Padding Mask 생성
xt = pad_sequence([torch.tensor(r["values"]) for r in tr], batch_first=True)
xv = pad_sequence([torch.tensor(r["values"]) for r in va], batch_first=True)
lt = torch.tensor([r["length"] for r in tr])
lv = torch.tensor([r["length"] for r in va])
yt = torch.tensor([r["label"] for r in tr])
yv = torch.tensor([r["label"] for r in va])

# 시점 인덱스가 실제 길이(lt, lv) 이상인 위치를 True(패딩)로 표시하는 마스크 [B, T]
mt = torch.arange(xt.size(1)).unsqueeze(0) >= lt.unsqueeze(1)
mv = torch.arange(xv.size(1)).unsqueeze(0) >= lv.unsqueeze(1)

# 3. ModuleDict를 활용한 Transformer 분류 파이프라인 구성
parts = nn.ModuleDict({
    "projection": nn.Linear(3, 8),
    "position": nn.Embedding(12, 8),
    "encoder": nn.TransformerEncoder(
        nn.TransformerEncoderLayer(8, 2, dim_feedforward=16, dropout=0, batch_first=True),
        1,
        enable_nested_tensor=False,
    ),
    "head": nn.Linear(8, 2),
})

optimizer = torch.optim.Adam(parts.parameters(), lr=0.01)

# 4. 학습 루프 (30 Epochs)
for epoch in range(30):
    parts.train()
    optimizer.zero_grad()
    # [핵심 포인트 1: Feature Projection + Positional Embedding 결합]
    # 3차원 입력 특성을 8차원으로 투영한 뒤, 각 시점 인덱스(0 ~ T-1)의 위치 임베딩을 브로드캐스팅으로 더합니다.
    embedded = parts["projection"](xt) + parts["position"](torch.arange(xt.size(1)))
    
    # TODO A06: Transformer에 실제 길이로 만든 Padding Mask를 전달한다.
    # 위치 임베딩은 값 임베딩과 더한다. masked mean에서는 Padding query도 제외한다.
    # BEGIN A06
    # [핵심 포인트 2: src_key_padding_mask를 통한 패딩 Key 차단]
    # 어텐션 연산 시 패딩 위치(mt=True)가 문맥 정보(Key)로 참조되지 않도록 마스크를 전달합니다.
    encoded = parts["encoder"](embedded, src_key_padding_mask=mt)
    # END A06
    
    # [핵심 포인트 3: Masked Mean Pooling]
    # 패딩 위치의 Query 출력 행을 (~mt)로 0으로 지운 뒤 실제 유효 길이(lt)로 나누어 문맥 벡터를 추출합니다.
    pooled = (encoded * (~mt).unsqueeze(-1)).sum(1) / lt.unsqueeze(-1)
    loss = nn.CrossEntropyLoss()(parts["head"](pooled), yt)
    loss.backward()
    optimizer.step()

# 5. 검증 데이터 평가 및 결과 저장
parts.eval()
with torch.inference_mode():
    embedded = parts["projection"](xv) + parts["position"](torch.arange(xv.size(1)))
    encoded = parts["encoder"](embedded, src_key_padding_mask=mv)
    pooled = (encoded * (~mv).unsqueeze(-1)).sum(1) / lv.unsqueeze(-1)
    pred = parts["head"](pooled).argmax(1)

print("train/valid:", len(tr), len(va), "위치 최대 길이:", 12)
print("params:", sum(p.numel() for p in parts.parameters()))
print("valid accuracy:", round((pred == yv).float().mean().item(), 3))
pd.DataFrame({
    "id": [r["id"] for r in va],
    "actual": yv.tolist(),
    "prediction": pred.tolist(),
}).to_csv(OUT / "transformer_predictions.csv", index=False)

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Position Embedding 결합:
   - Self-Attention은 순서에 불변(Permutation-invariant)하므로 nn.Embedding(12, 8)을 통해 시점 순서를 명시적으로 주입함.
2. 2중 마스킹(src_key_padding_mask + Masked Mean)의 일관성:
   - 학습과 평가 모두에서 패딩 Key를 차단하고 유효 시점 Query만 평균 풀링하여 가변 길이 시퀀스 왜곡을 완벽히 방지함.
==============================================================================
"""