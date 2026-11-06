# [Report] Day 15 비전 응용 통합 탐지·추적 데모 프로젝트 보고서

## 1. 실험 개요 및 고정 조건
- 목적: 제공된 정답 데이터와 사전 학습된 가중치를 활용해 객체 탐지, IoU 매칭, YOLO 학습/추론 및 추적 파이프라인의 정상 작동 검증
- 고정 조건: 
  - PyTorch 단일 스레드 (`torch.set_num_threads(1)`) 및 난수 시드 고정
  - 검증(valid) 및 테스트(test) 분할 원칙 준수 (test 누수 차단)
  - Windows 한글 경로 및 메모리 충돌 예방을 위한 안전 입출력 적용

## 2. 핵심 구현 모듈 요약
- 01_boxes.py: 픽셀 좌표(xyxy) 기반 OpenCV Bounding Box 시각화 및 원본 배열 보호(.copy())
- 02_iou.py: 1:1 그리디 매칭 알고리즘을 통한 TP/FP/FN 및 Precision, Recall 산출
- 03_labels.py & 04_train.py: YOLO TXT 라벨 파싱 및 1-Epoch Smoke Test 학습 파이프라인 검증
- 05_metrics.py & 06_predict.py: Pandas idxmax를 이용한 최고 mAP 에폭 탐색 및 model.predict Results 파싱
- 07_project.py: 전이학습(Head-only) 및 산출물(CSV, JSON, 혼동 행렬, Grad-CAM 히트맵) 자동 생성 파이프라인

## 3. 트러블슈팅 및 엔지니어링 이슈
- 이슈 1 (Windows 한글 경로 버그): 
  - 폴더명에 한글('01_기본필수')이 포함될 때 C++ 기반 OpenCV 함수(cv2.imread/imwrite)가 경로를 깨뜨려 파일을 찾지 못하는 현상 발생.
  - 해결: `cv2.imencode`와 파이썬 `Path.write_bytes()` 조합의 안전 헬퍼 함수(`save_image_safe`)를 적용하여 완벽 우회.
- 이슈 2 (Segmentation fault): 
  - 스크립트 종료 시점의 PyTorch autograd와 OpenCV 모듈 간 가비지 컬렉션 충돌 발생.
  - 해결: 버퍼 플러시 후 `os._exit(0)`을 호출하여 프로세스를 안전하게 종료함으로써 충돌 원천 차단.

## 4. 결론 및 향후 개선안
- 데이터 계약 검증, 후처리 NMS, 추적 상태 관리(persist)의 중요성을 확인하였으며, 향후 실제 현장 영상 데이터 적용 시 도메인 시프트(Domain Shift) 대응을 위한 추가 증강 및 데이터 수집 파이프라인 확장 필요.