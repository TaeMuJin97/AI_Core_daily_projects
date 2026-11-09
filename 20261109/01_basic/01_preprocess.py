"""실습 01: 정상 문서 3장을 Gray와 Otsu로 변환합니다. 원본을 덮어쓰지 않습니다."""
from pathlib import Path
import cv2

base = Path(__file__).resolve().parent
for name in ['doc01', 'doc02', 'doc03']:
    image = cv2.imread(str(base / f'{name}.png'))
    # 아래 두 줄만 완성합니다. 출력은 채널이 없는 (높이, 너비) 배열입니다.
    # 해설 B01
    # ① BGR → Grayscale 변환
    # OpenCV로 읽은 컬러 이미지(BGR, 3채널)를 흑백 이미지(1채널)로 변환
    # 색상 정보를 제거하고 밝기 정보(0~255)만 남김
    # 문서의 글자와 배경을 구분하기 위한 전처리
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # ② Otsu 알고리즘을 이용한 자동 이진화(Thresholding)
    # 이미지의 밝기 분포(히스토그램)를 분석하여 최적 임계값을 자동 결정
    #
    # gray              : 입력 Grayscale 이미지
    # 0                 : 초기 임계값 (Otsu 사용 시 자동 계산되므로 무시됨)
    # 255               : 임계값을 초과한 픽셀에 적용할 값 (흰색)
    # cv2.THRESH_BINARY : 임계값 초과 → 255(흰색), 이하 → 0(검정)
    # cv2.THRESH_OTSU   : 클래스 간 분산이 최대가 되는 임계값 자동 선택
    #
    # 반환값:
    # threshold : Otsu 알고리즘이 자동으로 계산한 임계값
    # binary    : 글자와 배경을 검정(0)과 흰색(255)으로 구분한 이미지
    threshold, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
# 해설 끝 B01
    cv2.imwrite(str(base / f'p01_{name}_gray.png'), gray)
    cv2.imwrite(str(base / f'p01_{name}_binary.png'), binary)
    print(name, 'shape:', gray.shape, 'threshold:', threshold)