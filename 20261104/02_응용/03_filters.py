"""
==============================================================================
[실습 보고서: 03_filters.py - 스무딩 필터(Gaussian vs Median) 적용에 따른 노이즈 억제 및 Canny Edge 검출 비교]
1. 실험 목적: 노이즈가 포함된 Grayscale 이미지에 Gaussian Blur와 Median Blur를 각각 적용한 뒤,
              후속 Canny Edge 검출 시 가짜 잡음 경계(False Edge)가 얼마나 줄어드는지 픽셀 수로 정량 비교함.
2. 고정 조건: 입력 이미지(data/noisy_gray.png, 1채널), Canny 임계값(threshold1=80, threshold2=160)
3. 변경 조건: 
   - original: 필터 미적용 원본
   - gaussian: cv2.GaussianBlur(gray, (5, 5), 0) (가우시안 가중 평균)
   - median: cv2.medianBlur(gray, 5) (5x5 영역 내 중앙값 선택)
4. 주요 산출물: 
   - outputs/p03_{name}.png (필터별 블러 처리 결과 이미지 3장)
   - outputs/p03_{name}_edge.png (필터별 Canny Edge 검출 결과 이미지 3장)
   - outputs/p03_edges.csv (필터 종류별 검출된 Edge 픽셀 수 비교표)
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

# 1. 노이즈가 포함된 이미지를 1채널 Grayscale([H, W])로 로드
gray = cv2.imread("data/noisy_gray.png", cv2.IMREAD_GRAYSCALE)

# >>> TODO A03
# 같은 gray에 Gaussian (5,5), sigmaX=0과 Median ksize=5를 각각 적용하세요.
# [핵심 포인트 1: GaussianBlur vs medianBlur 인자 형식 차이]
# GaussianBlur는 ksize를 (가로, 세로) 튜플인 (5, 5)로 받으며, sigmaX=0으로 두면 커널 크기에 맞춰 표준편차를 자동 계산합니다.
# 반면 medianBlur는 정방형 커널만 사용하므로 ksize를 튜플이 아닌 1보다 큰 단일 홀수 정수(5)로 받습니다.
gaussian = cv2.GaussianBlur(gray, (5, 5), 0)
median = cv2.medianBlur(gray, 5)
# <<< TODO A03

rows = []
for name, result in [
    ("original", gray),
    ("gaussian", gaussian),
    ("median", median),
]:
    # [핵심 포인트 2: Canny Edge 검출과 사전 스무딩(Blur)의 역할]
    # Canny(입력, 하위 임계값=80, 상위 임계값=160)는 밝기 변화율(미분값)이 큰 위치를 찾아 255(흰색)로 표시합니다.
    # 블러 없이 원본(original)을 그대로 넣으면 점 잡음(Salt-and-Pepper 노이즈)까지 전부 경계선으로 오검출됩니다.
    edge = cv2.Canny(result, 80, 160)
    cv2.imwrite(f"outputs/p03_{name}.png", result)
    cv2.imwrite(f"outputs/p03_{name}_edge.png", edge)
    
    # [새 함수: np.count_nonzero(edge)]
    # Canny 결과 배열(0 또는 255)에서 0이 아닌 픽셀(즉, 255인 Edge 픽셀)의 총개수를 셉니다.
    rows.append([name, int(np.count_nonzero(edge))])

with open("outputs/p03_edges.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["filter", "edge_pixels"])
    w.writerows(rows)

print(rows)
print("Edge가 많다고 무조건 좋지 않습니다. 잡음 경계일 수도 있습니다.")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 필터별 Edge 픽셀 수 비교 및 해석:
   - original: 노이즈 주변의 급격한 밝기 변화가 모두 Edge로 잡혀 edge_pixels 수가 비정상적으로 많게 측정됨.
   - gaussian: 가중 평균으로 노이즈를 누그러뜨려 가짜 Edge가 크게 줄어들지만, 강한 점 잡음의 흔적이 일부 남거나 실제 경계가 약간 흐려짐.
   - median: 주변 픽셀의 중앙값을 선택하므로 극단적인 흰색/검은색 점 잡음(Impulse Noise)을 완벽히 제거하면서
             실제 도형의 외곽선만 깔끔하게 남겨 가장 정제된 Edge 픽셀 수를 기록함.
2. 실무 시사점:
   - Edge 검출 전처리에서는 단순히 검출된 픽셀 수가 많은 것이 좋은 게 아니라,
     노이즈 특성에 맞는 Blur 필터를 선행 적용하여 '불필요한 잡음 경계'를 제거하는 것이 핵심임.
==============================================================================
"""