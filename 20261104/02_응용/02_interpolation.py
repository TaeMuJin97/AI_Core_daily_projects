"""
==============================================================================
[실습 보고서: 02_interpolation.py - 리사이즈 보간법(Interpolation)별 축소·확대 품질 및 왕복 오차 비교]
1. 실험 목적: 원본 이미지(320x240)를 (80x60)으로 1/4 축소했다가 다시 원본 크기(320x240)로 확대하는
              왕복(Round-trip) 리사이즈 실험을 통해 INTER_NEAREST, INTER_LINEAR, INTER_AREA의 특성을 비교함.
2. 고정 조건: 입력 이미지(data/scene.png, 320x240), 축소 크기 dsize=(80, 60), 복원 크기 dsize=(320, 240)
3. 변경 조건: 보간법(interpolation) 옵션 -> nearest, linear, area 3종 비교
4. 주요 산출물: 
   - outputs/p02_{method}_small.png (보간법별 80x60 축소 이미지 3장)
   - outputs/p02_{method}_large.png (보간법별 320x240 재확대 이미지 3장)
   - outputs/p02_interpolation.csv (보간법별 축소 너비, 높이, 원본 대비 왕복 MSE 기록표)
==============================================================================
"""

import csv
import os
from pathlib import Path
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)
Path("outputs").mkdir(exist_ok=True)

image = cv2.imread("data/scene.png")
rows = []

for name, method in [
    ("nearest", cv2.INTER_NEAREST),
    ("linear", cv2.INTER_LINEAR),
    ("area", cv2.INTER_AREA),
]:
    # >>> TODO A02
    # 현재 method를 사용해 (너비80, 높이60)으로 축소한 small을 만드세요.
    # [핵심 포인트 1: dsize=(Width, Height) 순서와 보간법 지정]
    # NumPy 배열의 shape는 (H=60, W=80, C=3)이지만, cv2.resize의 dsize는 (W=80, H=60) 순서로 넣습니다.
    # interpolation=method를 지정하지 않으면 기본값인 INTER_LINEAR가 적용되므로 반드시 명시합니다.
    small = cv2.resize(image, (80, 60), interpolation=method)
    # <<< TODO A02
    
    # 축소된 이미지를 다시 원본 크기(너비 320, 높이 240)로 확대 복원합니다.
    large = cv2.resize(small, (320, 240), interpolation=method)
    cv2.imwrite(f"outputs/p02_{name}_small.png", small)
    cv2.imwrite(f"outputs/p02_{name}_large.png", large)
    
    # [핵심 포인트 2: uint8 언더플로우(Underflow) 방지를 위한 float32 형변환]
    # 동일 원본과 크기일 때만 오차를 비교합니다. float 변환으로 uint8 차이의 순환을 피합니다.
    # uint8(0~255 부호 없는 정수) 상태에서 바로 뺄셈을 하면 음수가 255 근처의 큰 양수로 뒤집히므로(예: 10 - 20 = 246),
    # 반드시 float32 실수형으로 변환한 뒤 제곱 오차 평균(MSE)을 계산해야 합니다.
    mse = np.mean((image.astype(np.float32) - large.astype(np.float32)) ** 2)
    rows.append([name, small.shape[1], small.shape[0], round(float(mse), 4)])

with open("outputs/p02_interpolation.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["method", "width", "height", "roundtrip_mse"])
    w.writerows(rows)

print(rows)
print("왕복 MSE는 이 합성 이미지의 수치 비교이며 모델 성능이 아닙니다.")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Shape(H, W)와 dsize(W, H) 매핑 확인:
   - dsize=(80, 60)으로 리사이즈한 결과 배열 small.shape는 (60, 80, 3)이 되며,
     가로 너비(width)는 small.shape[1]=80, 세로 높이(height)는 small.shape[0]=60으로 정확히 기록됨.
2. 보간법별 특성 및 왕복 MSE 해석:
   - 축소 시에는 영역 평균을 반영하는 INTER_AREA가 정보 손실이 적고, 확대 시에는 INTER_LINEAR가 경계를 부드럽게 보간함.
   - 단, 한 번 축소되면서 이미 고주파 세부 정보가 손실되었으므로 재확대(large)하더라도 원본과 완벽히 같아질 수는 없음(왕복 MSE > 0).
==============================================================================
"""