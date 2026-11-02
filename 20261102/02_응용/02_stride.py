"""
===================================================================================================================
[실습 보고서: 02_stride.py - 합성곱 보폭(Stride)에 따른 출력 Shape 및 연산량(MACs) 비교]
1. 실험 목적: Conv2d에서 커널 이동 간격(stride: 1 vs 2)을 바꿨을 때, 
              출력 Feature Map의 공간 크기(H, W), 학습 파라미터 수, 실제 연산량(MACs)의 변화를 비교함[cite: 35, 36, 42, 114]
2. 고정 조건: 입력 [4, 3, 32, 32], in_channels=3, out_channels=8, kernel_size=3, padding=1[cite: 42, 114]
3. 변경 조건: 보폭 (stride = 1 vs stride = 2)[cite: 42, 114]
4. 주요 산출물: 보폭별 Shape·파라미터·MACs 비교표 (outputs/stride_comparison.csv)[cite: 114]
===================================================================================================================
"""

from pathlib import Path
import copy
import csv
import json
import time
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import pandas as pd

torch.manual_seed(42)
torch.set_num_threads(1)
root = Path(__file__).resolve().parent
out = root / "outputs"
out.mkdir(exist_ok=True)

# 32x32 크기의 RGB(채널 3) 컬러 이미지 4장으로 구성된 가상 배치 텐서를 생성합니다[cite: 32, 114].
x = torch.rand(4, 3, 32, 32)
rows = []
for stride in [1, 2]:
    torch.manual_seed(42)
    
    # BEGIN A02
    # TODO A02: 현재 반복의 stride를 Conv2d에 전달한다.
    # [핵심 모듈: nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)]
    # - in_channels=3: 입력 이미지의 채널 수 (RGB 3채널)[cite: 37, 38, 114]
    # - out_channels=8: 서로 다른 특징을 뽑아낼 커널(필터)의 개수 -> 출력 채널 수가 8이 됨[cite: 35, 37, 38, 114]
    # - kernel_size=3: 3x3 크기의 작은 창으로 국소 영역을 스캔함[cite: 33, 35, 114]
    # - stride=stride: 커널이 이동하는 간격 (1이면 한 칸씩 촘촘히, 2면 두 칸씩 건너뛰며 스캔)[cite: 35, 39, 114]
    # - padding=1: 입력 테두리에 0을 한 겹 둘러싸서, stride=1일 때 공간 크기(32x32)가 줄어들지 않고 유지되게 함[cite: 35, 36, 40, 114]
    conv = nn.Conv2d(3, 8, 3, stride=stride, padding=1)
    # END A02
    
    # 입력 x를 합성곱 층에 통과시켜 출력 Feature Map(y)을 얻습니다[cite: 34, 40, 114].
    y = conv(x)
    
    # [새 함수: p.numel()을 이용한 총 학습 파라미터 수 계산]
    # - numel()은 텐서 내부의 총 원소 개수(Number of Elements)를 반환합니다.
    # - 가중치(Weight) 개수: out_channels(8) * in_channels(3) * kH(3) * kW(3) = 216개[cite: 37, 40, 114]
    # - 편향(Bias) 개수: out_channels(8) = 8개 -> 총 224개 (stride 값과 무관하게 커널 크기가 같으므로 파라미터 수는 동일함!)[cite: 40, 114]
    params = sum(p.numel() for p in conv.parameters())
    
    # 1 MAC=곱셈 후 누적 1회. bias 덧셈은 제외하며 batch 전체 값이다.
    # [핵심 개념: MACs (Multiply-Accumulate Operations, 곱셈-누적 연산량)]
    # - 출력 픽셀(y.numel()) 1개를 만들기 위해서는 3채널 * 가로 3 * 세로 3 = 총 27번(3*3*3)의 곱셈-덧셈이 필요합니다[cite: 16, 37, 114].
    # - 따라서 전체 연산량(MACs)은 (출력 텐서의 전체 원소 수) * 27이 됩니다[cite: 114].
    macs = y.numel() * (3 * 3 * 3)
    rows.append(dict(stride=stride, shape=str(tuple(y.shape)), params=params, macs=macs))

print(pd.DataFrame(rows).to_string(index=False))
pd.DataFrame(rows).to_csv(out / "stride_comparison.csv", index=False)


"""
===========================================================================================================================
[실험 결과 요약 및 진단 보고]
1. 출력 Shape의 변화:
   - stride=1: [4, 8, 32, 32] -> padding=1 덕분에 공간 해상도(32x32)가 그대로 유지됨[cite: 36, 40, 114].
   - stride=2: [4, 8, 16, 16] -> 커널이 2칸씩 이동하여 가로·세로 공간 크기가 각각 1/2로 축소(Downsampling)됨[cite: 36, 39, 114].
2. 파라미터 수(params) vs 연산량(MACs) 핵심 인사이트:
   - 파라미터 수(224개): stride를 1에서 2로 바꿔도 커널 자체의 크기(8x3x3x3 + 8)는 변하지 않으므로 동일함[cite: 37, 40, 114].
   - 연산량(MACs): stride=2로 설정하면 출력 공간 면적(16x16)이 1/4(256 vs 1024)로 줄어들기 때문에, 
     실제 곱셈-누적 계산량(MACs)도 884,736회에서 221,184회로 정확히 1/4로 크게 감소함[cite: 114]!
===========================================================================================================================
"""