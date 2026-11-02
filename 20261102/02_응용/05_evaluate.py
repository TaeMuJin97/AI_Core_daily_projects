"""
===============================================================================================================
[실습 보고서: 05_evaluate.py - CNN 모델 학습 루프 구현 및 Best Checkpoint 기반 혼동행렬 평가]
1. 실험 목적: CNN 모델을 5 Epoch 동안 학습시키며 매 Epoch 종료 시 동일 조건(eval 모드)에서 Train/Valid 성능을 측정하고,
              Valid Loss가 가장 낮은 최적 가중치(Best State)를 복원하여 최종 혼동행렬(Confusion Matrix)을 산출함.
2. 고정 조건: 입력 해상도 Resize((32, 32)), Batch Size(16), 손실 함수(CrossEntropyLoss), 옵티마이저(AdamW, lr=0.01)
3. 핵심 구현: 
   - 학습 단계: optimizer.zero_grad() -> loss 계산 -> loss.backward() -> optimizer.step()
   - 모델 선택: 매 Epoch의 valid_loss를 비교하여 최저 손실 달성 시 copy.deepcopy(model.state_dict())로 가중치 백업
4. 주요 산출물: 
   - outputs/cnn_history.csv (Epoch별 train/valid 손실 및 정확도 기록)
   - outputs/confusion_matrix.csv (최적 모델 기준 실제 클래스 vs 예측 클래스 교차표)
   - outputs/cnn_predictions.csv (검증 데이터 개별 파일명, 실제 라벨, 예측 라벨 목록)
===============================================================================================================
"""

from pathlib import Path
import copy
import csv
import json
import time
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import pandas as pd

torch.manual_seed(42)
torch.set_num_threads(1)
root = Path(__file__).resolve().parent
out = root / "outputs"
out.mkdir(exist_ok=True)

# 1. 데이터셋 및 DataLoader 구성
# 모든 이미지를 32x32 크기로 통일하고 [C, H, W] 텐서(0.0~1.0)로 변환합니다.
transform = transforms.Compose([transforms.Resize((32, 32)), transforms.ToTensor()])
train = datasets.ImageFolder(root / "data" / "train", transform=transform)
valid = datasets.ImageFolder(root / "data" / "valid", transform=transform)

# 학습용 로더는 매 에폭 데이터 순서를 섞어주고(shuffle=True), 검증용 로더는 순서를 고정(shuffle=False)합니다.
train_loader = DataLoader(train, batch_size=16, shuffle=True, num_workers=0,
                          generator=torch.Generator().manual_seed(42))
valid_loader = DataLoader(valid, batch_size=16, shuffle=False, num_workers=0)

# 2. CNN 아키텍처 정의 (nn.Sequential)
# 입력: (B, 3, 32, 32)
# -> Conv1+Pool: (B, 16, 16, 16)
# -> Conv2+Pool: (B, 32, 8, 8)
# -> AdaptiveAvgPool2d(1): (B, 32, 1, 1) -> Flatten: (B, 32) -> Linear: (B, 2)
model = nn.Sequential(
    nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(32, 2),
)

# 3. 손실 함수 및 옵티마이저 설정
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=0.0)

history = []
best_loss = float("inf")

# 4. 학습(Train) 및 검증(Evaluation) 루프 (총 5 Epoch)
for epoch in range(1, 6):
    model.train()  # 모델을 학습 모드로 전환
    for images, labels in train_loader:
        optimizer.zero_grad()                 # 1) 이전 스텝의 기울기 초기화
        loss = loss_fn(model(images), labels) # 2) 순전파(Forward) 및 손실(Loss) 계산
        # BEGIN A05
        # TODO A05: loss 역전파와 가중치 갱신을 순서대로 실행한다.
        loss.backward()                       # 3) 역전파(Backward)로 각 가중치의 기울기 계산
        optimizer.step()                      # 4) 계산된 기울기로 가중치( 파라미터) 업데이트
        # END A05

    # 같은 epoch 말 모델을 eval 모드로 평가해 train/valid의 측정 조건을 맞춘다.
    model.eval()
    row = {"epoch": epoch}
    with torch.no_grad():  # 평가 시에는 불필요한 그래디언트 추적을 꺼서 메모리와 연산 속도를 최적화함
        for phase, loader in [("train", DataLoader(train, batch_size=16)), ("valid", valid_loader)]:
            total_loss, correct, count = 0.0, 0, 0
            for images, labels in loader:
                logits = model(images)
                # 배치 크기를 곱해 전체 샘플의 총 손실 합을 구한 뒤, 나중에 전체 샘플 수(count)로 나눠 정확한 평균을 계산함
                total_loss += loss_fn(logits, labels).item() * len(labels)
                # 클래스 차원(dim=1)에서 가장 큰 로짓 값을 가진 인덱스를 예측값으로 선택해 정답과 비교
                correct += (logits.argmax(1) == labels).sum().item()
                count += len(labels)
            row[phase+"_loss"] = total_loss/count
            row[phase+"_accuracy"] = correct/count
    history.append(row)

    # [핵심 포인트: Best Model Checkpointing]
    # 현재 에폭의 검증 손실(valid_loss)이 역대 최저치보다 낮으면 최적 가중치 상태를 깊은 복사(deepcopy)로 저장합니다.
    # 단순 대입(best_state = model.state_dict())을 하면 다음 에폭 학습 시 참조가 공유되어 값이 덮어씌워지므로 deepcopy가 필수입니다.
    if row["valid_loss"] < best_loss:
        best_loss, best_epoch = row["valid_loss"], epoch
        best_state = copy.deepcopy(model.state_dict())

# 5. 최적 가중치(Best Checkpoint) 복원 및 최종 혼동행렬(Confusion Matrix) 평가
model.load_state_dict(best_state)
model.eval()
actual, predicted = [], []
with torch.no_grad():
    for images, labels in valid_loader:
        actual.extend(labels.tolist())
        predicted.extend(model(images).argmax(1).tolist())

# 2x2 혼동행렬 생성: 행(truth)은 실제 정답 라벨, 열(guess)은 모델의 예측 라벨
cm = torch.zeros(2, 2, dtype=torch.long)
for truth, guess in zip(actual, predicted):
    cm[truth, guess] += 1

print(pd.DataFrame(history).round(4).to_string(index=False))
print("best epoch:", best_epoch)
print("혼동행렬 행=실제, 열=예측:\n", cm.tolist())
# cm.diag()는 주대각선 원소(정답을 맞힌 개수), cm.sum(1)은 행 방향 합계(실제 각 클래스의 전체 샘플 수)를 의미함
print("클래스별 정답 수:", cm.diag().tolist(), "/", cm.sum(1).tolist())

# 6. 결과물 CSV 저장
pd.DataFrame(history).to_csv(out / "cnn_history.csv", index=False)
pd.DataFrame(cm.numpy(), index=train.classes, columns=train.classes).to_csv(out / "confusion_matrix.csv")
pd.DataFrame(dict(file=[Path(p).name for p,_ in valid.samples], actual=actual, predicted=predicted)).to_csv(out / "cnn_predictions.csv", index=False)

"""
===========================================================================================================================================================
[실험 결과 요약 및 진단 보고]
1. 학습/평가 분리 및 동일 시점 측정:
   - 미니배치 학습 중 누적한 train_loss는 가중치가 실시간으로 변하는 도중의 평균이므로 에폭 종료 후의 모델 상태와 다름.
   - 따라서 에폭이 끝난 뒤 model.eval() 및 torch.no_grad() 상태에서 Train과 Valid를 동일한 기준으로 재측정하여 공정하게 비교함.
2. Best Checkpoint 복원 (copy.deepcopy):
   - 마지막 에폭(Epoch 5)이 항상 가장 좋은 일반화 성능을 보장하지 않으므로, valid_loss가 최소였던 시점의 가중치를 복원하여 과적합 위험을 방지함.
3. 혼동행렬(Confusion Matrix)을 통한 세부 진단:
   - 전체 정확도(Accuracy) 하나만 보는 것을 넘어, 대각선(cm.diag())과 비대각선 원소를 통해 특정 클래스(horizontal vs vertical)에 대한 편향이나 오분류 패턴을 정밀하게 확인함.
===========================================================================================================================================================
"""