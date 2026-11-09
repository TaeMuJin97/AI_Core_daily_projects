"""
==============================================================================
[실습 보고서: 01_preprocess.py - OCR 전처리를 위한 Grayscale 변환 및 Otsu 전역 이진화]
1. 실험 목적: 정상 문서 3장(doc01~doc03.png)을 읽어 색상 채널이 제거된 2차원(높이, 너비) Grayscale 배열과
              Otsu 자동 임계값 기반의 이진화(Binary) 배열로 변환한 뒤 원본과 분리하여 저장함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 원본 보존 원칙: 원본 이미지(doc01.png)를 덮어쓰지 않고, 전처리 산출물(p01_*_gray.png, p01_*_binary.png)을
     별도 파일로 저장하여 추후 OCR 오류 발생 시 원인 추적이 가능하도록 함.
   - 2차원 단일 채널 변환(cv2.cvtColor): 3채널 BGR 배열(H, W, 3)에 cv2.COLOR_BGR2GRAY를 적용하면
     채널 축이 없는 (높이, 너비) 형태의 2차원 8-bit 밝기 배열(0~255)이 반환됨.
   - Otsu 전역 이진화(cv2.threshold): 초기 임계값을 0으로 두고 cv2.THRESH_BINARY | cv2.THRESH_OTSU 플래그를 전달하면,
     픽셀 밝기 히스토그램에서 글자와 배경의 클래스 간 분산을 최대화하는 최적 임계값(threshold)을 자동 산출하고
     글자(0, 검정)와 배경(255, 흰색)으로 나뉜 이진 이미지(binary)를 함께 반환함.
3. 주요 산출물: p01_doc01~03_gray.png, p01_doc01~03_binary.png
==============================================================================
"""
"""실습 01: 정상 문서 3장을 Gray와 Otsu로 변환합니다. 원본을 덮어쓰지 않습니다."""
from pathlib import Path
import cv2

base = Path(__file__).resolve().parent
for name in ['doc01', 'doc02', 'doc03']:
    image = cv2.imread(str(base / f'{name}.png'))
    # 아래 두 줄만 완성합니다. 출력은 채널이 없는 (높이, 너비) 배열입니다.
# TODO B01
    # [핵심 구현 1: BGR 3채널 이미지를 단일 채널 Grayscale 배열(H, W)로 변환]
    # 스켈레톤의 더미 코드(image[:, :, 0] * 0)를 실제 색공간 변환 함수로 교체합니다.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # [핵심 구현 2: Otsu 알고리즘으로 최적 임계값(threshold) 자동 추정 및 이진화(binary) 수행]
    # - 첫 번째 인자(gray): 단일 채널 Grayscale 입력 이미지
    # - 두 번째 인자(0): 수동 기준값 (THRESH_OTSU 사용 시 무시되고 내부에서 자동 계산됨)
    # - 세 번째 인자(255): 임계값보다 밝은 픽셀(배경)에 부여할 최댓값
    # - 네 번째 인자: 이진화 방식(THRESH_BINARY)과 Otsu 자동 추정(THRESH_OTSU) 플래그 결합
    threshold, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
# TODO 끝 B01
    cv2.imwrite(str(base / f'p01_{name}_gray.png'), gray)
    cv2.imwrite(str(base / f'p01_{name}_binary.png'), binary)
    print(name, 'shape:', gray.shape, 'threshold:', threshold)