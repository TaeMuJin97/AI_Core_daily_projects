"""
==============================================================================
[실습 보고서: 04_thresholds.py - 고정 임계값(Fixed) vs 오츠(Otsu) 자동 이진화 및 형태학 Closing 후 전경 픽셀 수 비교]
1. 실험 목적: Grayscale 이미지를 고정 임계값(127)과 Otsu 알고리즘(자동 최적 임계값)으로 각각 이진화(Binary)하고,
              형태학 닫힘 연산(MORPH_CLOSE)을 적용해 전경 픽셀의 변화를 정량 비교함.
2. 고정 조건: 입력 이미지(data/scene.png, 1채널), 최대 밝기 값(255), 형태학 커널(MORPH_RECT, 3x3)
3. 변경 조건: 
   - fixed: 고정 임계값 thresh=127 적용
   - otsu: cv2.THRESH_OTSU 플래그를 통한 최적 임계값 자동 결정
4. 주요 산출물: 
   - outputs/p04_{name}_binary.png (이진화 결과 이미지 2장)
   - outputs/p04_{name}_close.png (형태학 Closing 적용 결과 이미지 2장)
   - outputs/p04_foreground.csv (방식별 결정된 임계값, 처리 전후 전경 픽셀 수 기록표)
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

# 1. 1채널 Grayscale 이미지 로드
gray = cv2.imread("data/scene.png", cv2.IMREAD_GRAYSCALE)

# 고정 임계값(Fixed Thresholding): 사용자가 지정한 127을 기준으로 전경(255)과 배경(0) 분리
fixed_t, fixed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# >>> TODO A04
# Otsu로 임계값을 자동 결정하세요. 반환값 두 개를 otsu_t와 otsu로 받습니다.
# [핵심 포인트 1: Otsu 자동 임계값 이진화]
# 픽셀 밝기 히스토그램의 분포를 분석해 두 봉우리 사이의 최적 임계값을 자동으로 찾아줍니다.
# 임계값 인자는 0으로 두며, cv2.THRESH_BINARY와 cv2.THRESH_OTSU를 더해서(또는 비트 연산으로) 지정합니다.
otsu_t, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# <<< TODO A04

# [핵심 포인트 2: 형태학 구조 요소(Structuring Element) 생성]
# 3x3 직사각형(MORPH_RECT) 커널을 만들어 형태학 연산 범위로 사용합니다.
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
rows = []

for name, threshold, binary in [("fixed", fixed_t, fixed), ("otsu", otsu_t, otsu)]:
    # [핵심 포인트 3: 형태학 닫힘 연산 (MORPH_CLOSE: 팽창 -> 침식)]
    # 전경(흰색, 255) 내부의 작은 검은색 구멍을 메우거나 끊어진 경계를 보완합니다.
    result = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    cv2.imwrite(f"outputs/p04_{name}_binary.png", binary)
    cv2.imwrite(f"outputs/p04_{name}_close.png", result)
    
    # 처리 전(before)과 후(after)의 흰색 전경(255) 픽셀 수를 각각 측정합니다.
    rows.append([
        name,
        int(threshold),
        int(np.count_nonzero(binary)),
        int(np.count_nonzero(result)),
    ])

with open("outputs/p04_foreground.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["method", "threshold", "before", "after"])
    w.writerows(rows)

print(rows)

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. Fixed vs Otsu 임계값 비교:
   - Fixed 방식은 사용자가 임의로 정한 127을 사용하므로 조명 상태에 따라 전경이 과다 또는 과소 검출될 수 있음.
   - Otsu 방식은 이미지 자체의 히스토그램 분산을 최소화하는 최적 임계값(otsu_t)을 스스로 찾아내어 안정적인 이진화 마스크를 생성함.
2. 형태학 닫힘 연산(Closing)의 효과:
   - before(이진화 직후)에 비해 after(Closing 후)의 픽셀 수가 미세하게 증가하거나 유지됨.
   - 이는 전경 내부의 구멍이 메워지면서 끊겼던 영역이 서로 연결되었음을 나타냄.
==============================================================================
"""