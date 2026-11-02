"""
==============================================================================
[실습 보고서: 04_transforms.py - Train 데이터 증강(Augmentation) vs Valid 결정론적 변환 비교]
1. 실험 목적: 학습용(Train) 파이프라인에는 무작위 변환(Augmentation)을 적용해 데이터 다양성을 확보하고,
              검증용(Valid) 파이프라인에는 고정된 전처리만 적용하여 평가의 재현성(일관성)을 보장하는 원리를 확인함.
2. 고정 조건: 입력 이미지(horizontal 첫 번째 샘플)[cite: 11], 출력 해상도 Resize((64, 64)), ToTensor() 변환[cite: 11]
3. 변경 조건: 
   - train_transform: RandomHorizontalFlip, RandomRotation(10), ColorJitter(brightness=0.15) 추가[cite: 11]
   - valid_transform: 무작위 요소 없이 Resize((64, 64))와 ToTensor()만 적용[cite: 11]
4. 주요 산출물: 
   - 콘솔 출력: valid 2회 호출 일치 여부(True), 텐서 Shape((3, 64, 64)), train 2회 호출 일치 여부(False)
   - 시각화 파일: outputs/augmentation_preview.png (valid 1장 + 무작위 증강된 train 3장 비교 이미지)[cite: 11]
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

from PIL import Image, ImageDraw

# horizontal 폴더의 첫 번째 이미지를 RGB 모드로 불러옵니다[cite: 11].
path = sorted((root / "data" / "train" / "horizontal").glob("*.png"))[0]
image = Image.open(path).convert("RGB")

# [핵심 포인트 1: 라벨 보존(Label-preserving) 데이터 증강 설계]
# 좌우반전(RandomHorizontalFlip)과 미세 회전(10도)은 '가로 줄무늬(horizontal)'라는 정답 라벨을 바꾸지 않습니다[cite: 11].
# 반면 90도 회전을 적용하면 가로 줄무늬가 세로 줄무늬(vertical)가 되어 라벨이 깨지므로 사용하면 안 됩니다[cite: 11].
train_transform = transforms.Compose([
    transforms.Resize((64, 64)),              # 공간 해상도를 64x64로 통일[cite: 11]
    transforms.RandomHorizontalFlip(),        # 50% 확률로 좌우 반전[cite: 11]
    transforms.RandomRotation(10),            # -10도 ~ +10도 사이로 무작위 미세 회전[cite: 11]
    transforms.ColorJitter(brightness=0.15),  # 밝기를 무작위로 미세 조정[cite: 11]
    transforms.ToTensor(),                    # PIL Image(HWC, 0~255) -> PyTorch Tensor(CHW, 0.0~1.0)[cite: 11]
])

# BEGIN A04
# TODO A04: valid에는 Resize와 ToTensor만 적용한다[cite: 11].
# [핵심 포인트 2: 검증/테스트 데이터의 결정론적(Deterministic) 전처리]
# 평가 기준이 매번 흔들리지 않도록 무작위 증강을 모두 빼고 크기 조정과 텐서 변환만 수행합니다[cite: 11].
valid_transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
])
# END A04

# 동일한 원본 이미지를 train_transform에 3번 통과시켜 서로 다른 3개의 증강 텐서를 생성합니다[cite: 11].
augmented = [train_transform(image) for _ in range(3)]

# 동일한 원본 이미지를 valid_transform에 2번 통과시켜 결과가 완전히 똑같은지 확인합니다[cite: 11].
v1, v2 = valid_transform(image), valid_transform(image)

# [시각화 비교 캔버스 생성]
# ToPILImage()를 통해 CHW 텐서를 다시 PIL 이미지로 되돌린 뒤 한 장의 캔버스에 나란히 붙여 저장합니다[cite: 11].
canvas = Image.new("RGB", (4*128, 150), "white")
draw = ImageDraw.Draw(canvas)
for i, tensor in enumerate([v1]+augmented):
    canvas.paste(transforms.ToPILImage()(tensor).resize((128,128)), (128*i,22))
    draw.text((128*i+5,4), "valid" if i==0 else f"train {i}", fill="black")
canvas.save(out / "augmentation_preview.png")

# [새 함수: torch.equal(tensor1, tensor2)] 두 텐서의 크기와 모든 원소 값이 완벽히 동일한지 True/False로 반환합니다[cite: 11].
print("valid 동일:", torch.equal(v1, v2))
print("shape:", tuple(v1.shape))
print("train 3개 동일 여부:", torch.equal(augmented[0], augmented[1]))

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. valid 동일 여부 (True): 
   - valid_transform은 확률적(Random) 연산이 전혀 없으므로 몇 번을 호출해도 100% 동일한 텐서(v1 == v2)를 반환함.
2. 출력 Shape ((3, 64, 64)): 
   - Resize((64, 64))와 ToTensor()를 거치면서 [C=3, H=64, W=64] 규격의 PyTorch 표준 텐서로 변환됨.
3. train 동일 여부 (False): 
   - train_transform은 호출될 때마다 회전 각도와 밝기, 반전 여부가 무작위로 달라지므로 매 에폭마다 새로운 변형 샘플을 모델에 공급함.
==============================================================================
"""