"""
==============================================================================
[실습 보고서: 01_channels.py - OpenCV BGR vs Matplotlib RGB 채널 순서 비교 및 통계 산출]
1. 실험 목적: OpenCV의 기본 색상 순서(BGR)와 시각화 도구(Matplotlib)의 색상 순서(RGB) 차이를 이해하고,
              cvtColor 변환 전후의 시각화 결과 비교 및 공간 축(H, W) 기준 채널별 평균 밝기를 산출함.
2. 고정 조건: 입력 이미지(data/scene.png), 출력 해상도 및 DPI(figsize=(5, 4), dpi=120)
3. 핵심 구현: 
   - cv2.cvtColor(image, cv2.COLOR_BGR2RGB)를 통해 원본(image) 훼손 없이 RGB 배열 생성
   - image.mean(axis=(0, 1))을 사용하여 세로(H=0축)와 가로(W=1축)에 대해 평균을 내어 [B, G, R] 채널별 평균 계산
4. 주요 산출물: 
   - outputs/p01_wrong.png (BGR 배열을 그대로 RGB로 해석해 빨강·파랑이 뒤바뀐 오류 이미지)
   - outputs/p01_correct.png (BGR -> RGB 정상 변환 후 시각화한 이미지)
   - outputs/p01_channels.csv (B, G, R 각 채널의 전체 픽셀 평균값 기록표)
==============================================================================
"""

import csv
import os
from pathlib import Path
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)
Path("outputs").mkdir(exist_ok=True)

# 1. 원본 이미지 로드 (OpenCV 기본값: [H, W, C] 형태의 BGR uint8 배열)
image = cv2.imread("data/scene.png")

# >>> TODO A01
# Matplotlib 표시 전에 BGR을 RGB로 변환하세요. 원본 image는 그대로 유지합니다.
# [핵심 포인트 1: 비파괴적 색공간 변환]
# cv2.cvtColor는 원본 image 메모리를 덮어쓰지 않고 채널 순서(0번 Blue <-> 2번 Red)가 맞바뀐 새 배열을 반환합니다.
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# <<< TODO A01

# 2. 색공간 순서 오류 비교 시각화 저장
# 각각 별도의 Figure입니다. 색공간 순서의 오류를 직접 비교합니다.
plt.figure(figsize=(5, 4))
plt.imshow(image)
plt.title("Wrong: BGR interpreted as RGB")
plt.axis("off")
plt.tight_layout()
plt.savefig("outputs/p01_wrong.png", dpi=120)
plt.close()

plt.figure(figsize=(5, 4))
plt.imshow(rgb)
plt.title("Correct: RGB display")
plt.axis("off")
plt.tight_layout()
plt.savefig("outputs/p01_correct.png", dpi=120)
plt.close()

# 3. 채널별 평균 밝기 계산 및 CSV 저장
# [핵심 포인트 2: 다중 축(axis=(0, 1)) 집계 연산]
# image의 Shape가 (H, W, 3)일 때, 0번 축(Height)과 1번 축(Width)을 동시에 평균 내면
# 공간 차원이 모두 압축되고 마지막 채널 차원(3)만 남아 [B평균, G평균, R평균] 1차원 배열이 도출됩니다.
means = image.mean(axis=(0, 1))

with open("outputs/p01_channels.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["channel", "mean"])
    w.writerows(zip(["B", "G", "R"], means))

print("BGR 채널평균:", np.round(means, 3).tolist())
# (y=30, x=30) 위치의 픽셀 값 확인: BGR 원본에서 [B, G, R]이던 값이 변환 후 [R, G, B] 순서로 출력됨
print("변환후 빨강:", rgb[30, 30].tolist())

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. BGR vs RGB 시각화 비교:
   - p01_wrong.png에서는 R(빨강) 값이 큰 픽셀이 첫 번째 채널(Blue 자리)이 아닌 세 번째 채널로 들어가 파란색으로 왜곡 표시됨.
   - COLOR_BGR2RGB 변환을 거친 p01_correct.png에서는 원래의 의도된 색상으로 정확히 복원됨.
2. 채널 통계 및 원본 보존 검증:
   - 원본 image 배열은 변환 후에도 그대로 BGR 순서를 유지하므로, image.mean(axis=(0, 1)) 결과는
     정확히 ["B", "G", "R"] 순서의 채널 평균과 1:1로 매칭됨.
==============================================================================
"""