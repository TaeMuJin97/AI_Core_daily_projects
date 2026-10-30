from pathlib import Path
import pandas as pd
import torch
from torch import nn

# CPU 연산 스레드 수를 1개로 고정하여 연산 결과의 일관성을 높입니다.
torch.set_num_threads(1)

# 현재 파일이 위치한 디렉터리 경로를 기준으로 데이터셋 파일(points.csv)의 절대 경로를 설정합니다.
base = Path(__file__).resolve().parent
df = pd.read_csv(base / "points.csv")

# 데이터셋을 학습용(train)과 검증용(valid)으로 분리합니다.
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]

# 학습 및 검증 데이터를 PyTorch Tensor 형태로 변환합니다. (입력은 float32, 레이블은 long)
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long)
# test 4건은 읽은 표에만 있으며 학습/평가 Tensor로 만들지 않습니다. (최종 평가 전까지 봉인)

# 학습률 후보 두 개를 리스트로 쓰세요: 0.001, 0.01.
# 모델·seed·20 epochs·AdamW·weight_decay=0은 그대로 둡니다.
# >>> B03
# TODO B03: 위 요구사항에 맞게 이 블록만 완성합니다.
learning_rates = [0.001, 0.01]
# <<< B03

# 다중/이진 분류 문제에 적합한 교차 엔트로피 손실 함수(CrossEntropyLoss)를 정의합니다.
loss_fn = nn.CrossEntropyLoss()

# 각 학습률(lr)별로 모델을 처음부터 학습시키며 성능을 비교하는 반복문입니다.
for lr in learning_rates:
    # 매번 동일한 초기 가중치(seed=42)에서 시작하도록 난수 생성기를 고정합니다.
    torch.manual_seed(42)
    
    # 입력 feature 2개 -> 은닉층 8개 -> ReLU 활성화 함수 -> 출력 2개(클래스 점수) 구조의 순차 신경망을 생성합니다.
    model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2))
    
    # 가중치 갱신을 담당할 Optimizer로 AdamW를 설정하고, 현재 학습률(lr)과 weight_decay=0.0을 적용합니다.
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.0)
    
    # 에폭별 검증 손실(valid loss) 값을 기록할 빈 리스트를 초기화합니다.
    losses = []
    
    # 총 20 에폭(Epoch) 동안 반복 학습을 진행합니다.
    for epoch in range(20):
        # 1. 모델을 학습 모드(train mode)로 전환합니다. (Dropout, BatchNorm 등의 동작에 영향)
        model.train()
        
        # 2. 이전 스텝에 누적된 기울기(gradient)를 초기화합니다.
        optimizer.zero_grad()
        
        # 3. 순전파(Forward)로 예측값을 구한 뒤 손실(Loss)을 계산하고, 즉시 역전파(Backward)를 통해 기울기를 계산합니다.
        loss_fn(model(X_train), y_train).backward()
        
        # 4. 계산된 기울기를 바탕으로 Optimizer가 가중치를 갱신(Step)합니다.
        optimizer.step()
        
        # 갱신이 끝난 모델의 valid loss를 기록합니다. valid로 backward하지 않습니다.
        # 5. 모델을 평가 모드(eval mode)로 전환합니다.
        model.eval()
        
        # 6. 평가 중에는 역전파가 필요 없으므로 gradient 계산을 비활성화하여 메모리를 절약합니다.
        with torch.no_grad():
            # 검증 데이터(X_valid)에 대한 loss를 계산하고 파이썬 스칼라 값(.item())으로 변환하여 리스트에 추가합니다.
            losses.append(loss_fn(model(X_valid), y_valid).item())
            
    # 해당 학습률(lr)에서의 결과 출력: 처음 5개의 에폭 손실 값과 마지막 20번째 에폭의 검증 손실을 반올림하여 출력합니다.
    print("lr:", lr, "처음 5개:", [round(x, 6) for x in losses[:5]])
    print("마지막 valid loss:", round(losses[-1], 6))