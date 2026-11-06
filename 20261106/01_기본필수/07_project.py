"""
==============================================================================
[실습 보고서: 07_project.py - YOLO 객체 탐지 및 ByteTrack 다중 객체 추적(MOT) 파이프라인 통합]
1. 실험 목적: 사전 준비된 가중치(demo.pt)를 활용해 검증 이미지 셋을 대상으로 객체 탐지(Predict)를 수행하고,
              동시에 동영상(demo.avi) 스트림에 ByteTrack 알고리즘을 연동하여 프레임 간 객체 고유 ID(Track ID)를 
              유지하며 궤적을 추적하고 결과를 CSV 및 영상으로 저장함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 객체 탐지 vs 추적(Tracking): 탐지는 각 프레임별 독립적인 위치(xyxy)와 클래스, 점수를 반환하며, 
     추적은 model.track()과 persist 상태 관리를 통해 연속된 프레임 간 동일 객체에 Track ID를 부여함.
   - 스트림 처리(stream=True): 긴 영상 처리 시 메모리 폭발(OOM)을 방지하기 위해 제너레이터 방식으로 프레임을 순차 처리함.
   - 트래커 상태 초기화: 새로운 영상 파일로 넘어갈 때는 이전 상태와 섞이지 않도록 새로운 모델 인스턴스로 트래커를 시작함.
3. 주요 산출물: p07_predictions.csv, p07_tracked.avi, p07_tracks.csv, p07_frames.csv
==============================================================================
"""
"""실습 07~08. 실제 모델의 이미지 탐지와 영상 추적을 연결합니다."""
from pathlib import Path
import cv2
import torch
import pandas as pd
from ultralytics import YOLO

# Windows 한글 폴더명('01_기본필수') 경로 우회를 위해 상대 경로 기준점 설정
BASE = Path(".")
torch.set_num_threads(1)

# 검증 이미지 탐지를 위한 YOLO 모델 객체 생성
model = YOLO(str(BASE / "data/demo.pt"))
rows = []

# 이미지 폴더 추론 후 예측 결과를 CSV로 저장
for r in model.predict(source=str(BASE/"data/images/val"), conf=0.25, imgsz=160, device="cpu", verbose=False):
    for box, cls, score in zip(r.boxes.xyxy.cpu().tolist(), r.boxes.cls.cpu().tolist(), r.boxes.conf.cpu().tolist()):
        rows.append([Path(r.path).name, int(cls), score, *box])
pd.DataFrame(rows, columns=["image", "class_id", "confidence", "x1", "y1", "x2", "y2"]).to_csv(BASE/"p07_predictions.csv", index=False)

# 새 영상은 새 모델 인스턴스로 시작하여 이전 추적 상태를 이어붙이지 않습니다.
tracker = YOLO(str(BASE / "data/demo.pt"))
cap = cv2.VideoCapture(str(BASE / "data/demo.avi"))
fps = cap.get(cv2.CAP_PROP_FPS)
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
cap.release()
writer = cv2.VideoWriter(str(BASE / "p07_tracked.avi"), cv2.VideoWriter_fourcc(*"MJPG"), fps, size)
tracks = []; frame_rows = []

# >>> B08
# 요구: demo.avi를 ByteTrack으로 읽는 stream=True 결과 generator를 만드세요.
# persist=False는 새로운 파일 스트림의 시작입니다. 같은 파일 내부 프레임은 이어집니다.
# [핵심 구현: model.track()을 통한 ByteTrack 연동 및 스트림 제너레이터 활성화]
results = tracker.track(
    source=str(BASE / "data/demo.avi"),
    tracker="bytetrack.yaml",
    conf=0.25,
    imgsz=160,
    device="cpu",
    persist=False,
    stream=True,
    verbose=False
)
# <<< B08

for frame, result in enumerate(results):
    writer.write(result.plot())
    frame_rows.append([frame, len(result.boxes)])
    if result.boxes.id is not None:
        for box, cls, score, tid in zip(result.boxes.xyxy.cpu().tolist(), result.boxes.cls.cpu().tolist(), result.boxes.conf.cpu().tolist(), result.boxes.id.cpu().tolist()):
            tracks.append([frame, int(tid), int(cls), score, *box])

writer.release()

# >>> B09
# 요구: tracks를 지정한 열 이름의 CSV로 저장하세요. index=False를 사용합니다.
# [핵심 구현: 프레임별 객체 트래킹 로그 DataFrame 변환 및 영구 저장]
pd.DataFrame(
    tracks, 
    columns=["frame", "track_id", "class_id", "confidence", "x1", "y1", "x2", "y2"]
).to_csv(BASE / "p07_tracks.csv", index=False)
# <<< B09

pd.DataFrame(frame_rows, columns=["frame", "detections"]).to_csv(BASE/"p07_frames.csv", index=False)
print("입력 fps/size:", fps, size, "처리 Frame:", len(frame_rows))
print("실습 08: 설정을 바꾸지 말고 다시 실행해 Frame 수·CSV·영상을 확인하세요.")