"""실습 07~08: 정상 데이터 20건. train 12건 학습, valid 4건 확인, test 4건 보관.

1. 데이터 준비 (Data Preparation): CSV 파일에서 데이터를 읽어 Train / Valid로 분할하고 Tensor로 변환
2. 모델 정의 (Model Definition): 인공신경망(ANN) 계층 구조 설계 (입력층 -> 은닉층 -> 출력층)
3. 손실 함수 & 최적화 (Loss & Optimizer): CrossEntropyLoss 및 SGD 설정
4. 학습 루프 (Training Loop): 에포크 반복, Forward -> Loss -> Backward -> Step 4단계 사이클
5. 모델 평가 (Evaluation): No-Grad 환경에서 검증 데이터로 모델 성능(정확도) 측정
6. 결과 저장 (Result Saving): 메트릭 및 학습 로그를 파일로 기록
"""

from pathlib import Path
import csv
import json
import torch
from torch import nn

# ==============================================================================
# 1. 데이터 로드 및 분할 (Data Preparation & Splitting)
# ==============================================================================
# Path(__file__).resolve().parent: 현재 파이썬 스크립트가 위치한 절대 경로를 구합니다.
# 이렇게 경로를 지정하면 터미널의 현재 위치(Current Working Directory)에 상관없이 항상 안전하게 파일을 읽을 수 있습니다.
base = Path(__file__).resolve().parent

# CSV 파일을 딕셔너리 리스트 형태로 한 줄씩 읽어옵니다.
with (base / "points.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

# [중요 - 데이터 분할 (Data Split)]
# - train (학습용): 모델의 가중치(weight)를 갱신하는 데 직접 사용 (12건)
# - valid (검증용): 학습에 참여하지 않고, 모델이 처음 보는 데이터에 대해 잘 동작하는지 중간 점검 (4건)
# - test (평가용): 최종 배포 전 단 한 번만 평가하기 위해 여기서는 Tensor로 변환하지 않고 보관 (4건, 데이터 누수 방지)
train_rows = [r for r in rows if r["split"] == "train"]
valid_rows = [r for r in rows if r["split"] == "valid"]

# [PyTorch Tensor 변환]
# - 입력 특성(X): 모델의 행렬 곱 연산을 위해 소수점 연산이 가능한 'float32' 타입 Tensor로 생성
# - 레이블 정답(y): nn.CrossEntropyLoss가 정수형 클래스 인덱스(0, 1, ...)를 요구하므로 'torch.long'(int64)으로 설정
# - X_train Shape: (12, 2) -> 12개의 샘플, 각 샘플당 2개의 입력 특성 [x1, x2]
# - y_train Shape: (12,)   -> 12개의 정답 레이블 [0 또는 1]
X_train = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in train_rows])
y_train = torch.tensor([int(r["label"]) for r in train_rows], dtype=torch.long)

X_valid = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in valid_rows])
y_valid = torch.tensor([int(r["label"]) for r in valid_rows], dtype=torch.long)

# ==============================================================================
# 2. 모델 구조 정의 (Model Definition)
# ==============================================================================
# 난수 시드(seed) 고정: 매번 코드를 실행할 때마다 모델 가중치의 초기값이 동일하게 생성되도록 하여
# 실험 결과의 재현성(Reproducibility)을 보장합니다.
torch.manual_seed(42)

# [ANN(인공신경망) Sequential 모델]
# 데이터 흐름: 입력(2개) -> 선형변환(2->8) -> 비선형 활성화함수(ReLU) -> 선형변환(8->2) -> 출력 Logit(2개)
# 1) nn.Linear(2, 8): 2개의 입력을 8개의 은닉 노드로 선형 변환 (가중치 2*8 + 편향 8 = 24개 파라미터)
# 2) nn.ReLU(): 비선형 활성화 함수 max(0, z). 복잡한 결정 경계(비선형 패턴)를 학습할 수 있게 해줌
# 3) nn.Linear(8, 2): 8개의 은닉 특성을 받아 최종 2개 클래스(0과 1)에 대한 점수(Logit)를 출력 (8*2 + 2 = 18개)
# 총 학습 가능한 파라미터(Weight + Bias) 수: 24 + 18 = 42개
model = nn.Sequential(
    nn.Linear(2, 8),
    nn.ReLU(),
    nn.Linear(8, 2)
)

# ==============================================================================
# 3. 손실 함수(Loss Function) 및 최적화(Optimizer) 설정
# ==============================================================================
# [nn.CrossEntropyLoss()]
# - 다중 클래스/이진 분류에서 표준적으로 사용하는 손실 함수
# - [주의]: 내부에 이미 Softmax 계산이 포함되어 있으므로, 모델 마지막 출력층에 별도로 nn.Softmax()를 붙이지 않습니다!
loss_fn = nn.CrossEntropyLoss()

# [torch.optim.SGD (확률적 경사 하강법)]
# - model.parameters(): 모델 내부의 학습 가능한 가중치(W)와 편향(b)들을 옵티마이저에 전달
# - lr=0.1 (Learning Rate, 학습률): 기울기(Gradient) 반대 방향으로 얼마나 크게 보폭을 내딛을지 결정
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

# 학습 시작 전(epoch 0)의 초기 손실값(loss)을 기록해둡니다.
# .item(): 원소가 1개인 스칼라 텐서에서 순수 파이썬 float 숫자를 추출할 때 사용
history = [[0, loss_fn(model(X_train), y_train).item()]]

# ==============================================================================
# 4. 학습 루프 (Training Loop - 80 Epochs)
# ==============================================================================
# model.train(): 모델을 '학습 모드'로 설정합니다.
# (Dropout, BatchNorm 등의 레이어가 있을 때 학습 모드로 동작하게 함. 현재 모델엔 없으나 좋은 습관)
model.train()

# Full-batch 학습: 여기서는 12개의 train 데이터를 미니배치로 쪼개지 않고 한 번에 모두 입력하여 학습합니다.
for epoch in range(1, 81):
    # [학습 4단계 사이클]
    # 1단계: 기울기 초기화 (Zero Grad)
    # PyTorch는 기본적으로 .backward() 호출 시 기울기를 누적(accumulate)하므로,
    # 새로운 반복(iteration)마다 반드시 이전 배치의 기울기를 0으로 비워주어야 합니다.
    optimizer.zero_grad()

    # 2단계: 순전파 (Forward Pass) 및 손실 계산 (Loss Computation)
    # model(X_train)을 통해 예측값(Logits, shape: [12, 2])을 얻고, 정답 y_train([12])과 비교하여 손실 스칼라 계산
    loss = loss_fn(model(X_train), y_train)

    # >>> B08
    # TODO
    # 3단계: 역전파 (Backward Pass)
    # 계산 그래프를 따라 손실값에 대한 각 파라미터의 미분값(기울기, gradient)을 계산하여 param.grad에 저장합니다.
    loss.backward()

    # 4단계: 파라미터 갱신 (Optimizer Step)
    # 계산된 gradient와 학습률(lr)을 바탕으로 가중치를 실제로 갱신합니다: W_new = W_old - (lr * W_grad)
    optimizer.step()
    # <<< B08

    # [학습 경과 모니터링]
    # 가중치가 갱신된 직후 모델의 손실값을 다시 측정하여 기록합니다.
    # torch.no_grad(): 평가 목적이므로 불필요한 미분 계산 그래프 생성을 막아 메모리와 연산량을 절약합니다.
    with torch.no_grad():
        history.append([epoch, loss_fn(model(X_train), y_train).item()])

# ==============================================================================
# 5. 모델 검증 및 평가 (Validation & Evaluation)
# ==============================================================================
# model.eval(): 모델을 '평가(추론) 모드'로 전환합니다.
# ※ 주의: model.eval()만으로는 미분 계산 그래프(gradient)가 꺼지지 않으므로, 아래의 torch.no_grad()와 항상 함께 사용합니다.
model.eval()

with torch.no_grad():
    # 검증 데이터 4건에 대한 모델의 로짓(Logits) 출력 (Shape: [4, 2])
    # logits의 각 행: [클래스0 점수, 클래스1 점수]
    logits = model(X_valid)

    # >>> B09
    # TODO
    # [클래스 예측 (Argmax)]
    # 점수(logit)가 더 큰 쪽의 클래스 번호(0 또는 1)를 최종 예측값으로 채택합니다.
    # dim=1: 행 방향(가로, 클래스 축)으로 비교하라는 의미 (Shape: [4, 2] -> [4])
    prediction = logits.argmax(dim=1)
    # <<< B09

    # [정확도 계산 (Accuracy)]
    # 1) (prediction == y_valid): boolean 텐서 [True, False, ...]
    # 2) .float(): 계산을 위해 1.0과 0.0으로 형변환
    # 3) .mean(): 전체 정답 비율(평균) 계산
    # 4) .item(): 파이썬 실수값으로 추출
    accuracy = (prediction == y_valid).float().mean().item()

# ==============================================================================
# 6. 결과 파일 저장 및 메트릭 기록 (Output & Logging)
# ==============================================================================
# 1) 학습 손실 추이 저장 (training_history.csv)
with (base / "training_history.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "train_loss_eval"])
    writer.writerows(history)

# 2) 최종 평가지표 및 예측 결과 메타데이터 구성 (final_metrics.json)
metrics = {
    "device": "cpu",
    "epochs": 80,
    "train_rows": 12,
    "valid_rows": 4,
    "test_used": False,              # 테스트 데이터는 검증에 절대 사용하지 않음 (오염 방지)
    "valid_accuracy": accuracy,
    "initial_train_loss": history[0][1],
    "final_train_loss": history[-1][1],
    "valid_ids": [r["id"] for r in valid_rows],
    "actual": y_valid.tolist(),
    "predicted": prediction.tolist()
}
(base / "final_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

# 3) PyTorch 및 실행 하드웨어 환경 정보 기록 (gpu_check.txt)
(base / "gpu_check.txt").write_text(
    f"torch={torch.__version__}\ncuda_build={torch.version.cuda}\n"
    f"cuda_available={torch.cuda.is_available()}\nselected_device=cpu\n",
    encoding="utf-8"
)

# 콘솔에 최종 결과 출력
print("분할: train 12 / valid 4 / test 4(보관)")
print("train loss:", round(history[0][1], 6), "->", round(history[-1][1], 6))
print("valid 정확도:", round(accuracy, 4))
print("valid 예측:", prediction.tolist())
print("생성: gpu_check.txt, training_history.csv, final_metrics.json")
