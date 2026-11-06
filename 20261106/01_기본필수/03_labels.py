"""
==============================================================================
[실습 보고서: 03_labels.py - YOLO TXT 라벨 포맷 파싱 및 이미지-라벨 1:1 매칭 검증]
1. 실험 목적: 학습용 이미지 6장과 그에 대응하는 YOLO 표준 TXT 라벨 파일을 읽어,
              정규화된 중심 좌표(cx, cy)와 크기(width, height) 및 클래스 ID를 파싱하고 구조를 확인함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 파일명 1:1 대응 규칙 (stem 활용): YOLO 데이터셋은 images/train/xxx.png에 대해
     labels/train/xxx.txt처럼 확장자만 제외한 파일 이름(image_path.stem)이 정확히 일치해야 함.
   - YOLO TXT 포맷 구조: 헤더나 주석 없이 객체 1개당 한 줄씩 'class_id cx cy w h' 5개의 숫자를 공백으로 구분해 저장함.
     이때 좌표 4개는 원본 이미지의 가로(W)·세로(H)로 나눈 0~1 범위의 정규화(Normalized) 실수값임.
   - 빈 줄 방어 및 줄 분리: read_text(encoding="utf-8").splitlines()를 사용하면 운영체제별 줄바꿈 문자(\r\n, \n)나
     파일 끝의 불필요한 개행을 깔끔하게 처리하여 라인 리스트를 얻을 수 있음.
==============================================================================
"""
"""실습 03. 정상 이미지 6장과 YOLO TXT 라벨을 읽습니다."""
from pathlib import Path
import cv2

# [트러블슈팅: 한글 폴더명('01_기본필수')에서 cv2.imread가 깨지는 현상 방지]
# 절대 경로(resolve)를 쓰면 상위 한글 폴더명이 포함되어 OpenCV C++ 로더가 None을 반환합니다.
# 원래 코드를 주석 처리하고 현재 작업 디렉터리 기준 상대 경로(".")를 사용합니다.
# BASE = Path(__file__).resolve().parent
BASE = Path(".")

# 클래스 ID(0, 1, 2)를 실제 도형 이름으로 변환하기 위한 매핑 리스트
names = ["square", "circle", "triangle"]

# sorted()를 통해 운영체제에 상관없이 항상 동일한 파일 순서로 상위 6장을 가져옵니다.
for image_path in sorted((BASE / "data/images/train").glob("*.png"))[:6]:
    image = cv2.imread(str(image_path))
    
    # [핵심 개념 1: Path.stem을 이용한 이미지-라벨 1:1 경로 연결]
    # image_path.name은 'img_01.png'이지만, image_path.stem은 확장자를 뺀 'img_01'만 반환합니다.
    # 여기에 '.txt'를 붙여 labels/train 폴더 내의 짝꿍 라벨 파일 경로를 정확히 조합합니다.
    label_path = BASE / "data/labels/train" / (image_path.stem + ".txt")
    
    # >>> B04
    # 요구: UTF-8 라벨 파일의 문자열을 읽고 줄 목록으로 나누세요.
    # [핵심 개념 2: UTF-8 텍스트 읽기 및 줄 단위 리스트 변환]
    # - read_text(encoding="utf-8"): 파일을 열고 닫는(open/close) 과정을 한 줄로 안전하게 처리합니다.
    # - .splitlines(): 문자열을 줄바꿈 기준으로 쪼개어 리스트로 만듭니다.
    #   (참고: .split("\n")과 달리 파일 맨 마지막에 빈 줄바꿈이 있어도 빈 문자열("") 원소를 만들지 않아 안전합니다.)
    lines = label_path.read_text(encoding="utf-8").splitlines()
    # <<< B04
    
    # image.shape는 (Height, Width, Channel)를 의미하며, len(lines)는 해당 이미지 안의 정답 객체(Box) 개수입니다.
    print(image_path.name, "shape:", image.shape, "boxes:", len(lines))
    
    for line in lines:
        # [핵심 개념 3: YOLO 한 줄 문자열('class_id cx cy w h') 언패킹]
        # 공백 기준으로 쪼갠 5개의 문자열을 모두 float으로 변환한 뒤 각 변수에 할당합니다.
        # cls도 일단 float(예: 0.0)으로 읽히므로 리스트 인덱싱을 할 때는 반드시 int(cls)로 정수 변환해야 합니다.
        cls, cx, cy, width, height = map(float, line.split())
        print(" ", names[int(cls)], "normalized:", cx, cy, width, height)