# 🚀 AI Core Engineer Daily Projects

매일 진행하는 AI / 딥러닝 실습 코드와 개념 주석, 실험 결과를 기록하는 통합 저장소입니다.

## 📂 일자별 학습 목차 및 아카이브

- **[Day 01 (2026-10-19)](./20261019/)**: 과정 OT, VS Code·Python·가상환경 구성 및 Git 기초
- **[Day 02 (2026-10-20)](./20261020/)**: Python 조건문·반복문, 디버깅 기초, 함수와 스코프
- **[Day 03 (2026-10-21)](./20261021/)**: NumPy 배열 연산과 Pandas 정제·집계 기초
- **[Day 04 (2026-10-22)](./20261022/)**: NumPy/Pandas 심화 및 Matplotlib 시각화, CSV·JSON 처리
- **[Day 05 (2026-10-23)](./20261023/)**: 머신러닝 문제정의, 전처리 Pipeline 및 데이터 분할
  - [💬 팀원 피드백 및 리뷰 기록](https://github.com/TaeMuJin97/20261023_07project) *(보존 레포)*
- **[Day 06 (2026-10-26)](./20261026/)**: 선형·로지스틱 회귀, KNN 회귀·분류 및 하이퍼파라미터 비교
  - [💬 팀원 피드백 및 리뷰 기록](https://github.com/TaeMuJin97/20261026_07project) *(보존 레포)*
- **[Day 07 (2026-10-27)](./20261027/)**: Decision Tree, Random Forest, XGBoost와 과적합 제어
  - [💬 팀원 피드백 및 리뷰 기록](https://github.com/TaeMuJin97/20261027_project) *(보존 레포)*
- **[Day 08 (2026-10-28)](./20261028/)**: 평가지표(Accuracy~ROC), 교차검증, 특성설계 및 K-Means 군집화
  - [💬 팀원 피드백 및 리뷰 기록](https://github.com/TaeMuJin97/20261028_project) *(보존 레포)*
- **[Day 09 (2026-10-29)](./20261029/)**: GPU(CUDA) Tensor, Autograd 역전파, 기본 ANN 학습 루프 구현
  - [💬 팀원 피드백 및 리뷰 기록](https://github.com/TaeMuJin97/20261029_project) *(보존 레포)*
- **[Day 10 (2026-10-30)](./20261030/)**: Optimizer(SGD, AdamW), Learning Rate Scheduler, 과적합 정규화(Dropout, BatchNorm, Early Stopping)
  - **주요 학습 내용**: Optimizer 갱신 규칙 비교, ReduceLROnPlateau 스케줄러 연동, Early Stopping best 모델 복원 구현
- **[Day 11 (2026-11-03)](./20261103/)**: Convolution Neural Networks (CNN) 심화 및 커스텀 Dataset/DataLoader 구축
  - **주요 학습 내용**: 이미지 텐서 변환(Transforms), nn.Conv2d/MaxPool2d 채널 차원 변화 실습, PyTorch Dataset 상속 및 커스텀 데이터 로딩 구현
- **[Day 12 (2026-11-04)](./20261104/)**: Pre-trained Model 활용 및 전이학습(Transfer Learning)
  - **주요 학습 내용**: torchvision.models 사전학습 모델 구조 분석, Feature Extractor 동결(Freeze) 및 Head-only 미세조정(Fine-tuning) 구현
- **[Day 13 (2026-11-05)](./20261105/)**: 객체 탐지(Object Detection) 기초와 Bounding Box 및 IoU/NMS
  - **주요 학습 내용**: xyxy/xywh 좌표계 변환, IoU(Intersection over Union) 수동 계산, NMS(Non-Maximum Suppression) 후처리 로직 구현
- **[Day 14 (2026-11-06)](./20261106/)**: YOLO 객체 탐지 모델 학습 및 추론 파이프라인
  - **주요 학습 내용**: dataset.yaml 데이터 계약 설정, Ultralytics YOLO 1-Epoch Smoke Test 학습, model.predict 결과 파싱 및 시각화
- **[Day 15 (2026-11-07)](./20261107/)**: 다중 객체 추적(MOT: Multi-Object Tracking)과 모델 산출물 자동화
  - **주요 학습 내용**: ByteTrack 알고리즘을 활용한 동영상 스트림 `model.track()` 연동, Track ID 유지 궤적 추적, 모델 평가 지표 및 Grad-CAM 시각화 자동화 파이프라인 구축
- **[Day 16 (2026-11-09)](./20261109/)**: OCR 문서 전처리부터 VLM 질의응답 및 엣지 배포 설계
  - **주요 학습 내용**: OpenCV Grayscale/Otsu 이진화/원근 보정, Tesseract OCR 단어별 Box·신뢰도 추출, 정규표현식을 활용한 JSON 구조화 및 업무 규칙 검증, VLM 멀티모달 대화 템플릿 처리 및 OCR-VLM 근거(Grounding) 대조, TensorRT-Jetson-DeepStream 엣지 배포 아키텍처 설계
