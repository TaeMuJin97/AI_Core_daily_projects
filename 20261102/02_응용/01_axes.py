"""
==============================================================================
[실습 보고서: 01_axes.py - 이미지 Tensor의 축(Axes) 변환과 시각화 규격 비교]
1. 실험 목적: PyTorch 표준 이미지 규격인 CHW를 시각화 도구(Matplotlib)용 HWC로 변환하고,
              다시 모델 입력용 배치 규격인 NCHW로 복원하며 데이터 무결성을 검증함[cite: 31, 32, 115]
2. 핵심 함수: transforms.ToTensor(), tensor.permute(), tensor.unsqueeze(), torch.equal()[cite: 31, 60, 115]
3. 주요 산출물: HWC 변환 시각화 이미지 (outputs/image_axes.png)[cite: 115]
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

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# [새 기능: Path.glob("*.png") 및 PIL Image 로드]
# horizontal 폴더 내의 모든 png 파일 경로를 찾아 이름순(sorted)으로 정렬한 뒤 첫 번째 이미지를 선택합니다[cite: 115].
path = sorted((root / "data" / "train" / "horizontal").glob("*.png"))[0]

# [핵심 변환: PIL Image -> transforms.ToTensor()]
# 1) Image.open(path).convert("RGB"): 이미지를 열어 3채널(RGB) PIL 객체로 맞춥니다[cite: 115].
# 2) transforms.ToTensor(): 일반 이미지의 축 순서인 [H, W, C] (0~255 정수)를 
#    PyTorch 표준 규격인 [C, H, W] (0.0~1.0 사이의 float32 실수) Tensor로 자동 변환합니다[cite: 60, 115].
chw = transforms.ToTensor()(Image.open(path).convert("RGB"))

# BEGIN A01
# TODO A01: 채널 축을 마지막으로 보내 HWC를 만든다.
# [핵심 함수: tensor.permute(*dims)]
# - 역할: 기존 Tensor의 차원(축) 순서를 원하는 인덱스 순서대로 재배열합니다[cite: 31].
# - 이유: PyTorch는 [C(0), H(1), W(2)]를 쓰지만, Matplotlib(plt.imshow)은 채널이 맨 뒤에 있는 [H, W, C] 형태만 그릴 수 있습니다[cite: 31, 32, 115].
# - 동작: 기존 1번 축(H), 2번 축(W), 0번 축(C) 순서로 재배치하여 [H, W, C]를 만듭니다[cite: 31, 115].
hwc = chw.permute(1, 2, 0)
# END A01

# [핵심 함수: permute() + unsqueeze(dim) 조합으로 NCHW 만들기]
# 1) hwc.permute(2, 0, 1): 현재 [H(0), W(1), C(2)] 상태에서 2번 축(C)을 맨 앞으로 가져와 다시 [C, H, W]로 되돌립니다[cite: 31, 115].
# 2) .unsqueeze(0): CNN 모델은 항상 배치 단위 입력([N, C, H, W])을 받으므로, 0번 위치(맨 앞)에 크기 1짜리 배치(N=1) 축을 추가합니다[cite: 27, 31, 115].
nchw = hwc.permute(2, 0, 1).unsqueeze(0)

plt.figure(figsize=(4, 4))
# Tensor를 NumPy 배열(.numpy())로 변환하여 HWC 상태로 화면(파일)에 그립니다[cite: 115].
plt.imshow(hwc.numpy())
plt.title("HWC view: horizontal stripes")
plt.axis("off") # 이미지 주변의 가로·세로 눈금 축을 숨깁니다[cite: 115].
plt.tight_layout()
plt.savefig(out / "image_axes.png", dpi=120)
plt.close()

print("CHW / HWC / NCHW:", tuple(chw.shape), tuple(hwc.shape), tuple(nchw.shape))
# [새 함수: torch.equal(tensor1, tensor2)]
# 두 텐서의 크기(Shape)와 모든 원소의 값이 완벽히 일치하는지 비교하여 True/False를 반환합니다.
# 축을 이리저리 바꿨다가 되돌려도(chw vs nchw[0]) 원본 픽셀 데이터가 전혀 손상되지 않았음을 검증합니다[cite: 115].
print("왕복 값 일치:", torch.equal(chw, nchw[0]))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 축(Axes) 규격 차이: 
   - PyTorch 연산 표준: CHW [3, H, W] 및 배치 단위 NCHW [1, 3, H, W][cite: 31, 32, 115]
   - 이미지 출력(Matplotlib/PIL) 표준: HWC [H, W, 3][cite: 31, 32, 60, 115]
2. 데이터 보존 확인: permute()와 unsqueeze()는 내부 픽셀 값을 바꾸지 않고 축의 시점(View)과 
   차원만 조작하므로, 왕복 변환 후에도 원본 텐서와 완벽히 일치(True)함[cite: 31, 115].
==============================================================================
"""