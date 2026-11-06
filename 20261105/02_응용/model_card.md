# Model Card: Day 14 전이학습 및 불균형 분류 통합 프로젝트

> **작성일:** 2026-11-05  
> **모델 유형:** 컴퓨터 비전 이미지 분류 (합성 도형 3클래스: `circle`, `square`, `triangle`)  
> **기반 아키텍처:** TinyShapeCNN (사전학습 Backbone) + Linear Head  

---

## 1. 모델 개요 및 목적 (Model Overview)
본 모델은 소규모 합성 비전 데이터를 대상으로 **사전학습 Backbone 재사용(전이학습)**, **미세조정(Fine-tuning) 범위 제어**, 그리고 **클래스 불균형(Class Imbalance) 대응** 전략이 분류 성능과 소수 클래스 재현율(Recall)에 미치는 영향을 체계적으로 검증하기 위해 구축되었습니다. 
* **엄격한 평가 원칙**: 모델 성능 비교 및 하이퍼파라미터 선택은 오직 **Validation Set**을 기준으로 수행되었으며, 최종 평가 전까지 **Test Set은 일절 개봉하지 않았습니다(`test_used: False`)**.

---

## 2. 실험 전략 및 비교 군 (Experiment Strategies)
동일한 초기 시드(`seed=14`)와 8 Epoch 학습 예산 하에서 총 3가지 전략을 비교했습니다.

1. **Head-only (`strategy="head", balance="none"`)**: 
   * Backbone 전체를 동결(`requires_grad=False`)하고 새로 교체한 분류 Head(`model[9]`, 파라미터 771개)만 학습합니다.
2. **Partial Fine-tuning (`strategy="partial", balance="none"`)**: 
   * Head와 함께 두 번째 합성곱 층(`model[4]`, 파라미터 1,152개)의 동결을 해제하여 총 1,923개의 파라미터를 미세조정합니다.
3. **Head + Class Weight (`strategy="head", balance="weight"`)**: 
   * Head-only 구조를 유지하되, 학습 데이터의 클래스 역빈도(Inverse Frequency) 기반 가중치를 계산하여 `nn.CrossEntropyLoss(weight=...)`에 반영함으로써 소수 클래스 오분류 페널티를 강화합니다.

---

## 3. 정량 성과 지표 (Quantitative Results)

| 실험 전략 | 불균형 대응 | 학습 파라미터 수 | 최적 에폭 (Best Epoch) | 검증 정확도 (Accuracy) | Macro F1 | 소수 클래스 (triangle) Recall |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Head-only** | None | 771개 | 8 | 0.8111 | 0.8100 | 0.7000 |
| **Partial FT** | None | 1,923개 | 6 | 0.7889 | 0.7850 | 0.6333 |
| **Head + Weight** | Class Weight | 771개 | 7 | 0.8333 | 0.8300 | 0.7667 |

* **해석**: 단순 모델 용량을 키우는 Partial Fine-tuning보다, 손실 함수에서 소수 클래스 기여도를 직접 보정해 준 **Head + Class Weight** 전략이 **Macro F1($0.8300$)**과 **triangle Recall($0.7667$)** 측면에서 가장 균형 잡힌 우수한 성능을 기록했습니다.

---

## 4. 단계별 산출물 구성 (Artifacts)
실행 파이프라인(`07_project_3.py`)은 학습 종료 후 다음 산출물들을 `outputs/` 폴더에 자동으로 생성합니다.
* `metrics.csv` / `history.csv`: 전체 실험 군별 지표 요약표 및 에폭별 Valid Loss 추이
* `predictions.csv`: 검증 셋 전체 샘플의 실제값, 예측값, 모델 확신도(Confidence) 기록표
* `confusion.csv`: 실제 클래스 $\times$ 예측 클래스 교차 행렬 (Confusion Matrix)
* `project_error_*.png`: 모델이 오분류한 대표 이미지 타일 모음 (최대 8장)
* `project_cam.png`: 첫 번째 오답 샘플에 대한 Grad-CAM 히트맵 오버레이 ($256 \times 256$)

---

## 5. 한계점 및 향후 개선 과제 (Limitations & Future Work)
1. **도메인 확장성 한계**: 본 실험은 제어된 합성 도형 데이터를 사용했으므로, 조명 변화, 잡음, 복잡한 배경이 존재하는 실제 자연 이미지(Natural Images) 환경에서도 동일한 가중치/샘플러 효과가 유지되는지 추가 검증이 필요합니다.
2. **소표본 데이터의 과적합 위험**: Partial Fine-tuning 시 일부 상위 층을 열었을 때 데이터가 부족하면 쉽게 과적합(Overfitting) 조짐이 나타날 수 있으므로, 향후 데이터 증강(Data Augmentation) 파이프라인과의 결합 실험이 요구됩니다.