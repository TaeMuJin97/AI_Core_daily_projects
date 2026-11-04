from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)

import csv

# 결과 이름의 p07_ 접두어가 입력 파일 덮어쓰기를 방지합니다.
rows = []
for filename in ["scene.png", "noisy.png", "objects.png"]:
    image = cv2.imread(filename)
    # >>> 해설 B07
    # 단계별 파일을 남겨 무엇이 달라졌는지 눈으로 확인합니다. 원본320×240과 출력160×120은 같은 가로세로 비율입니다.
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (160, 120), interpolation=cv2.INTER_AREA)
    # <<< 해설 B07
    # >>> 해설 B08
    # 이 프로젝트에서는 단순한 처리 흐름을 익히기 위해 필터는 추가하지 않습니다.
    edge = cv2.Canny(small, 80, 160)
    # <<< 해설 B08
    stem = Path(filename).stem
    cv2.imwrite(f"p07_{stem}_gray.png", gray)
    cv2.imwrite(f"p07_{stem}_small.png", small)
    cv2.imwrite(f"p07_{stem}_edge.png", edge)
    rows.append([filename, image.shape[1], image.shape[0], small.shape[1], small.shape[0], int(np.count_nonzero(edge))])

cap = cv2.VideoCapture("sample.avi")
fps = cap.get(cv2.CAP_PROP_FPS)
writer = cv2.VideoWriter("p07_video.avi", cv2.VideoWriter_fourcc(*"MJPG"), fps, (160, 120))
print("Writer:", writer.isOpened())
count = 0
while cap.isOpened() and writer.isOpened():
    ok, frame = cap.read()
    if not ok:
        break
    # >>> 해설 B09
    # 출력 Writer의 frameSize=(160,120)과 쓰는 프레임의 shape가 일치해야 합니다. FPS12와 프레임48을 유지하므로 재생시간4초입니다.
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_small = cv2.resize(frame_gray, (160, 120), interpolation=cv2.INTER_AREA)
    frame_edge = cv2.Canny(frame_small, 80, 160)
    # <<< 해설 B09
    writer.write(cv2.cvtColor(frame_edge, cv2.COLOR_GRAY2BGR))
    count += 1
cap.release()
writer.release()
with open("p07_summary.csv", "w", encoding="utf-8-sig", newline="") as f:
    output = csv.writer(f)
    output.writerow(["source", "source_w", "source_h", "output_w", "output_h", "edge_pixels"])
    output.writerows(rows)

# 실습08: 파일을 실제로 다시 읽습니다. 성공 메시지만으로 완료 판단하지 않습니다.
check = cv2.VideoCapture("p07_video.avi")
print("이미지 수/Frame 수:", len(rows), count)
print("재읽기 이미지 Shape:", cv2.imread("p07_scene_edge.png", 0).shape)
print("재읽기 영상 Frame/FPS:", int(check.get(cv2.CAP_PROP_FRAME_COUNT)), check.get(cv2.CAP_PROP_FPS))
check.release()
print("결과: p07_ PNG 9개 + AVI 1개 + CSV 1개")
