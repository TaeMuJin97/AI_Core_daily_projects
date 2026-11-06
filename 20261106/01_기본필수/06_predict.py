"""
==============================================================================
[실습 보고서: 06_predict.py - 사전 준비된 YOLO 모델로 검증 이미지 추론 및 결과 아티팩트 저장]
1. 실험 목적: 미리 준비된 가중치(demo.pt)를 로드하여 검증 이미지 폴더(data/images/val)를 대상으로
              추론(Predict)을 수행하고, 탐지 결과(Boxes, Confidence, Class)를 CSV 및 이미지로 저장함.
2. 핵심 개념 및 엔지니어링 포인트:
   - model.predict() 인자 제어: source(입력 경로), conf=0.25(신뢰도 25% 이상만 필터링), 
     imgsz=160(추론 입력 해상도), device="cpu"(실습 환경 통일) 설정.
   - Results API 파싱: 추론 결과로 반환된 Results 객체 리스트를 순회하며, 
     boxes.xyxy(픽셀 좌표), boxes.cls(클래스 ID), boxes.conf(신뢰도)를 
     CPU 텐서 및 넘파이 리스트(.cpu().tolist())로 안전하게 변환하여 추출함.
3. 주요 산출물: p06_predictions.csv, p06_counts.csv, p06_[이미지명].png (시각화 결과)
==============================================================================
"""
"""실습 06. 강사가 준비한 실제 도형 YOLO weight로 valid 이미지만 추론합니다."""
from pathlib import Path
import cv2
import torch
import pandas as pd
from ultralytics import YOLO

# BASE = Path(__file__).resolve().parent
BASE = Path(".")  # 한글 폴더명 경로 우회용 상대 경로 설정

torch.set_num_threads(1)

# data/demo.pt는 교실 사전 준비 도구로 생성합니다. 임의 모델로 자동 대체하지 않습니다.
model = YOLO(str(BASE / "data/demo.pt"))

rows = []
counts = []

# >>> B07
# 요구: data/images/val을 conf=0.25, imgsz=160, CPU로 predict 하세요.
# source는 입력 경로, conf/imgsz/device는 선택 인자입니다.
# [핵심 구현: model.predict() 추론 파이프라인 호출]
# - source: 검증 이미지들이 위치한 디렉터리 경로
# - conf=0.25: 불필요한 배경 노이즈를 거르고 신뢰도 0.25 이상인 후보만 남김
# - imgsz=160: 160x160 크기로 리사이즈하여 추론 속도 최적화
# - device="cpu": CPU 환경에서 안전하게 연산 수행
results = model.predict(
    source=str(BASE / "data/images/val"),
    conf=0.25,
    imgsz=160,
    device="cpu"
)
# <<< B07

for result in results:
    name = Path(result.path).stem
    counts.append({"image": name, "detections": len(result.boxes)})
    
    # result.plot()은 OpenCV BGR 배열 형태로 탐지 박스가 그려진 이미지를 반환합니다.
    cv2.imwrite(str(BASE / ("p06_" + name + ".png")), result.plot())
    
    # 각 탐지 객체별로 xyxy 픽셀 좌표, 클래스 ID, 신뢰도 점수를 추출하여 리스트에 담습니다.
    for box, cls, score in zip(result.boxes.xyxy.cpu().tolist(), result.boxes.cls.cpu().tolist(), result.boxes.conf.cpu().tolist()):
        rows.append([name, int(cls), score, *box])

# 분석 결과를 후속 활용을 위해 CSV 파일로 영구 저장합니다.
pd.DataFrame(rows, columns=["image", "class_id", "confidence", "x1", "y1", "x2", "y2"]).to_csv(BASE / "p06_predictions.csv", index=False)
pd.DataFrame(counts).to_csv(BASE / "p06_counts.csv", index=False)
print("처리 이미지:", len(counts), "탐지 수:", len(rows))