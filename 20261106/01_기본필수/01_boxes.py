"""
==============================================================================
[실습 보고서: 01_boxes.py - Bounding Box 좌표 체계 이해 및 OpenCV 시각화 기초]
1. 실험 목적: 원본 이미지(scene.png)와 정답 라벨(boxes_gt.csv)을 읽어, 픽셀 단위 xyxy 좌표를
              OpenCV의 cv2.rectangle 함수로 이미지 위에 정확히 그리고 별도 파일로 저장함.
2. 핵심 개념 및 주의점:
   - 원본 보존 원칙: cv2.rectangle 등 OpenCV 그리기 함수는 입력 배열(ndarray)의 메모리를 직접 덮어쓰는
     In-place 연산을 수행함. 따라서 반드시 image.copy()로 복사본을 만들어 작업해야 원본이 훼손되지 않음.
   - xyxy 좌표계: 왼쪽 위 시작점 (x1, y1)과 오른쪽 아래 끝점 (x2, y2)의 정수(int) 픽셀 좌표를 사용함.
   - BGR 색상 순서: Matplotlib이나 PIL은 RGB 순서를 쓰지만, OpenCV는 BGR(Blue, Green, Red) 순서를 사용함.
3. 주요 산출물: p01_boxes.png (정답 박스 3개가 그려진 결과 이미지)
==============================================================================
"""
"""실습 01. 정답 박스 3개를 그립니다. 원본 scene.png는 바꾸지 않습니다."""
from pathlib import Path
import cv2
import pandas as pd

# 기존: BASE = Path(__file__).resolve().parent  (절대 경로라 '01_기본필수'가 포함됨)
BASE = Path(".")  # 현재 위치 기준 상대 경로 ('data/scene.png'로만 전달되어 한글이 안 섞임!)
image = cv2.imread(str(BASE / "data/scene.png"))
boxes = pd.read_csv(BASE / "data/boxes_gt.csv")

# [핵심 개념 1: 원본 이미지 배열 보호를 위한 깊은 복사(.copy())]
# 만약 result = image 처럼 단순 대입하면 두 변수가 같은 메모리 주소를 가리키게 되어 원본이 수정됩니다.
# .copy()를 호출해 독립된 메모리 공간에 배열을 복제합니다.
result = image.copy()  # 그릴 배열을 복사하여 원본을 보존합니다.

for row in boxes.itertuples():
    # >>> B01
    # 요구: result에 (x1,y1)~(x2,y2) 박스를 두께 2로 그리세요.
    # cv2.rectangle의 이미지·두 점·색은 필수, thickness는 선택입니다.
    # [핵심 개념 2: cv2.rectangle 인자 규격과 픽셀 좌표 캐스팅]
    # - 첫 번째 인자(result): 그림을 그릴 대상 이미지 배열
    # - 두 번째/세 번째 인자: 왼쪽 위 꼭짓점 (x1, y1)과 오른쪽 아래 꼭짓점 (x2, y2) 튜플.
    #   DataFrame에서 읽은 값이 실수(float)나 numpy 타입일 수 있으므로 안전하게 파이썬 int로 변환합니다.
    # - 네 번째 인자(color): BGR 순서의 색상 튜플. (255, 0, 0)은 파란색(Blue), (0, 255, 0)은 초록색입니다.
    # - 다섯 번째 인자(thickness): 선 두께(2 픽셀). 참고로 -1을 주면 사각형 내부를 색으로 가득 채웁니다.
    cv2.rectangle(
        result,
        (int(row.x1), int(row.y1)),
        (int(row.x2), int(row.y2)),
        (255, 0, 0),
        2
    )
    # <<< B01
    # 정답(Ground Truth) 박스는 사람이 직접 라벨링한 참값이므로 모델의 예측 점수(Confidence)가 존재하지 않습니다(N/A).
    print("class:", row.class_id, "xyxy:", row.x1, row.y1, row.x2, row.y2, "GT confidence: N/A")

cv2.imwrite(str(BASE / "p01_boxes.png"), result)
# OpenCV 이미지의 shape는 (Height, Width, Channel) 순서로 출력됩니다. (좌표계 x=Width, y=Height 순서와 반대임에 주의!)
print("shape:", image.shape, "저장: p01_boxes.png")