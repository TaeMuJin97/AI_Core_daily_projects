"""
==============================================================================
[실습 보고서: 03_downsample.py - MaxPool2d vs Stride 2 Conv2d 다운샘플링 비교]
1. 실험 목적: Feature Map의 공간 크기(H, W)를 절반(1/2)으로 줄이는 두 가지 대표적인 방식인
              MaxPool2d(2)와 Conv2d(stride=2)의 출력 Shape 및 학습 파라미터 수 차이를 비교함
2. 고정 조건: 입력 Tensor [4, 8, 32, 32] (배치 4, 채널 8, 32x32 해상도)
3. 변경 조건: 다운샘플링 방식 ("pool": MaxPool2d(2) vs "conv_stride2": Conv2d(8, 8, 3, stride=2, padding=1))
4. 주요 산출물: 다운샘플링 방식별 Shape 및 파라미터 비교표 (outputs/downsample_comparison.csv)
==============================================================================
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

# 8개의 채널(Feature Map)을 가진 32x32 크기의 가상 입력 데이터 4장을 준비합니다.
x = torch.rand(4, 8, 32, 32)

# [핵심 비교 모듈: nn.MaxPool2d vs stride=2 nn.Conv2d]
# 1) "pool" - nn.MaxPool2d(kernel_size=2): 
#    - stride를 생략하면 기본값으로 kernel_size(2)와 동일하게 설정됩니다 (즉, 2칸씩 이동).
#    - 2x2 영역 안에서 가장 큰 값(최대 반응) 하나만 남기므로, 별도의 학습 가중치(파라미터)가 전혀 없습니다(0개).
# 2) "conv_stride2" - nn.Conv2d(8, 8, 3, stride=2, padding=1):
#    - 3x3 커널을 2칸 간격(stride=2)으로 이동시키며 합성곱을 수행해 공간 크기를 줄입니다.
#    - 단순 최대값 추출이 아니라, 어떻게 공간을 압축할지 가중치(8*8*3*3 + 8 = 584개)를 통해 직접 학습합니다.
operations = {"pool": nn.MaxPool2d(2), "conv_stride2": nn.Conv2d(8, 8, 3, stride=2, padding=1)}
rows = []

# [새 문법: dict.items()] 딕셔너리에서 키(name)와 값(layer 모듈 객체)을 동시에 꺼내어 반복합니다.
for name, layer in operations.items():
    # BEGIN A03
    # TODO A03: 각 downsampling 층을 입력 x에 적용한다.
    # PyTorch의 모든 nn.Module 층(MaxPool2d, Conv2d 등)은 함수처럼 layer(x) 형태로 호출하면 내부 forward()가 실행됩니다.
    y = layer(x)
    # END A03
    rows.append(dict(method=name, shape=str(tuple(y.shape)), params=sum(p.numel() for p in layer.parameters())))

print(pd.DataFrame(rows).to_string(index=False))
pd.DataFrame(rows).to_csv(out / "downsample_comparison.csv", index=False)

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 출력 Shape 일치: 
   - pool (MaxPool2d)과 conv_stride2 모두 입력 [4, 8, 32, 32]를 받아 
     채널 수(8)는 유지하고 가로·세로 공간 크기만 절반으로 줄인 [4, 8, 16, 16]을 출력함.
2. 학습 파라미터(params)의 결정적 차이:
   - pool (MaxPool2d): 정해진 규칙(영역 내 최대값 선택)만 수행하므로 학습 파라미터가 0개임 (연산·메모리 절약에 유리).
   - conv_stride2: 채널 간 조합과 공간 축소를 동시에 학습하므로 584개의 파라미터가 필요함 (표현력은 높으나 파라미터 증가).
==============================================================================
"""