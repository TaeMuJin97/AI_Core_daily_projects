"""
==============================================================================
[실습 보고서: 05_video_sampling.py - 영상 프레임 샘플링(Frame Subsampling) 주기에 따른 처리량 및 재생시간 보존 검증]
1. 실험 목적: 입력 영상을 매 1번째(전수) 및 매 3번째(샘플링) 프레임마다 전처리(Resize -> Gray -> Canny Edge)하여 저장할 때,
              원본 재생시간을 유지하기 위한 출력 FPS 조정 원리와 실제 소요 시간(Decode+처리+Encode)을 비교함.
2. 고정 조건: 입력 영상(data/sample.avi), 출력 해상도 dsize=(160, 120), 코덱(MJPG), Canny 임계값(80, 160)
3. 변경 조건: 프레임 샘플링 간격 every = [1, 3] 및 이에 비례한 output_fps = fps / every 설정
4. 주요 산출물: 
   - outputs/p05_every1.avi, outputs/p05_every3.avi (샘플링 주기별 Edge 처리 영상)
   - outputs/p05_sampling.csv (디코딩 수, 저장 수, 재오픈 확인 프레임 수, FPS, 입출력 재생시간, 처리 속도 기록표)
==============================================================================
"""

import csv
import os
from pathlib import Path
from time import perf_counter
import cv2

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)
Path("outputs").mkdir(exist_ok=True)

rows = []
for every in [1, 3]:
    cap = cv2.VideoCapture("data/sample.avi")
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # >>> TODO A05
    # 매 every번째 frame만 저장해도 원래 재생시간을 유지하도록 output_fps를 계산하세요. 이 입력은 48이 1·3으로 나누어떨어집니다.
    # [핵심 포인트 1: 프레임 샘플링과 재생시간(Duration) 보존 공식]
    # 영상 재생시간(초) = 총 프레임 수 / FPS 입니다.
    # 매 every번째 프레임만 추출하면 저장 프레임 수가 (1 / every)배로 줄어들므로,
    # output_fps도 (fps / every)로 비례해서 낮춰야 빨리 감기(배속) 현상 없이 원본 재생시간이 유지됩니다.
    output_fps = fps / every
    # <<< TODO A05
    
    path = f"outputs/p05_every{every}.avi"
    # [핵심 포인트 2: VideoWriter 설정 규격]
    # frameSize는 NumPy 배열 shape(120, 160)의 반대인 (가로 W=160, 세로 H=120) 순서로 지정합니다.
    # 마지막 인자 isColor의 기본값은 True(3채널 BGR)입니다.
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), output_fps, (160, 120))
    
    read_count, written = 0, 0
    start = perf_counter()
    
    while cap.isOpened() and writer.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        # 프레임 인덱스가 every로 나누어떨어질 때만 전처리 및 인코딩(저장)을 수행합니다.
        if read_count % every == 0:
            small = cv2.resize(frame, (160, 120), interpolation=cv2.INTER_AREA)
            edge = cv2.Canny(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), 80, 160)
            
            # [핵심 포인트 3: 1채널 Edge 결과를 3채널 BGR로 복원 후 저장]
            # Canny의 결과(edge)는 1채널(H, W)이지만, VideoWriter는 기본 3채널(isColor=True)로 열렸으므로
            # COLOR_GRAY2BGR로 채널 수를 맞춰주어야 저장 오류가 발생하지 않습니다.
            writer.write(cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR))
            written += 1
        read_count += 1
        
    # 자원 해제 (호출하지 않으면 영상 파일 헤더가 정상적으로 닫히지 않음)
    cap.release()
    writer.release()
    seconds = perf_counter() - start
    
    # [핵심 포인트 4: 저장된 결과 영상 재오픈(Re-open) 검증]
    # 파일이 깨지지 않고 의도한 프레임 수(actual_count)와 FPS(actual_fps)로 저장되었는지 다시 열어서 검증합니다.
    check = cv2.VideoCapture(path)
    actual_count = int(check.get(cv2.CAP_PROP_FRAME_COUNT))
    actual_fps = check.get(cv2.CAP_PROP_FPS)
    check.release()
    
    rows.append([
        every,
        read_count,
        written,
        actual_count,
        actual_fps,
        read_count / fps,
        actual_count / actual_fps,
        seconds,
        written / seconds,
    ])
    print(f"N={every}: 읽기{read_count}, 저장{actual_count}, fps={actual_fps}, 출력초={actual_count/actual_fps:.2f}")

with open("outputs/p05_sampling.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "every",
        "decoded",
        "written",
        "reopened",
        "fps",
        "input_duration_s",
        "output_duration_s",
        "wall_s",
        "processed_fps",
    ])
    w.writerows(rows)

print("시간은 decode+처리+encode 포함. 모든 입력은 decode하므로 N배 가속을 보장하지 않습니다.")

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 프레임 수 및 재생시간 보존 검증:
   - every=1일 때: 48프레임 전체를 저장하고 원래 FPS를 유지하여 원본 재생시간과 동일함.
   - every=3일 때: 저장 프레임 수가 16장(48/3)으로 줄어들지만, output_fps도 1/3로 낮추었기 때문에
     출력 영상의 재생시간(output_duration_s = 16 / actual_fps)이 원본 재생시간과 정확히 일치함.
2. 왜 every=3으로 건너뛰어도 전체 소요 시간(wall_s)이 1/3로 줄어들지 않는가?
   - 전처리(Resize, Canny)와 인코딩(writer.write) 횟수는 1/3로 줄어들지만,
     while 루프에서 cap.read()를 통해 48개 모든 프레임을 읽고 압축 해제(Decode)하는 작업은 동일하게 수행되기 때문임.
==============================================================================
"""