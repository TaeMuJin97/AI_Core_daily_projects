
"""
Day14 실습: CNN 분류 모델의 혼동행렬 및 오분류 분석

[실습 목적]
사전학습된 CNN의 Head만 학습한 후, 검증 데이터에서 발생한
오분류를 확인하고 모델이 어떤 클래스를 혼동하는지 분석합니다.

[주요 동작]
1. Train/Valid 이미지 로딩 및 전처리
2. TinyShapeCNN 모델 생성 및 사전학습 Backbone 가중치 로딩
3. Backbone 동결(Freeze) 후 분류 Head만 1 Epoch 학습
4. 검증 데이터에 대한 클래스별 예측 결과 생성
5. 혼동행렬(Confusion Matrix)과 Classification Report 출력
6. 실제 오답 이미지 중 최대 3개의 파일명과 예측 결과 확인

[주의사항]
- Test 데이터는 사용하지 않습니다.
- 모델의 오류를 관찰하기 위해 1 Epoch만 학습합니다.
- Head만 학습하며 Backbone의 가중치와 BN 통계는 고정합니다.
- 본 실습은 최종 모델 성능평가가 아닌 오분류 분석 실습입니다.
"""

from pathlib import Path
import numpy as np
import torch
from torch import nn
from torchvision.datasets import ImageFolder
from torchvision import transforms as tr
from sklearn.metrics import confusion_matrix, classification_report


# ============================================================
# 1. 실행 환경 및 경로 설정
# ============================================================

torch.set_num_threads(1)
torch.manual_seed(14)

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE


# ============================================================
# 2. 데이터 로딩 함수
# ============================================================

def load_data():
    """
    Train/Valid 이미지를 읽고 학습 가능한 Tensor로 변환합니다.
    Test 데이터는 읽지 않습니다.
    """

    # RGB 이미지를 32×32 크기로 변환하고 픽셀값을 [0,1]로 변환
    transform = tr.Compose([
        tr.Resize((32, 32)),
        tr.ToTensor()
    ])

    # 클래스별 폴더 구조에서 이미지와 라벨을 자동으로 읽음
    train = ImageFolder(DATA / "train", transform=transform)
    valid = ImageFolder(DATA / "valid", transform=transform)

    # 이미지들을 하나의 Batch Tensor로 구성
    X_train = torch.stack([
        train[i][0] for i in range(len(train))
    ])
    y_train = torch.tensor(train.targets, dtype=torch.long)

    X_valid = torch.stack([
        valid[i][0] for i in range(len(valid))
    ])
    y_valid = torch.tensor(valid.targets, dtype=torch.long)

    return train, valid, X_train, y_train, X_valid, y_valid


# ============================================================
# 3. CNN 모델 생성 함수
# ============================================================

def create_model():
    """
    TinyShapeCNN을 생성하고 사전학습된 Backbone 가중치를 로딩합니다.
    Backbone은 동결하고 마지막 분류 Head만 학습 가능하도록 설정합니다.
    """

    model = nn.Sequential(

        # [Stage 1] 기초 특징 추출
        nn.Conv2d(3, 8, 3, padding=1, bias=False),  # [0]
        nn.BatchNorm2d(8),                          # [1]
        nn.ReLU(),                                  # [2]
        nn.MaxPool2d(2),                            # [3]

        # [Stage 2] 마지막 특징 추출 Stage
        nn.Conv2d(8, 16, 3, padding=1, bias=False), # [4]
        nn.BatchNorm2d(16),                         # [5]
        nn.ReLU(),                                  # [6]

        # [특징 집약] 16×4×4 → 256차원 벡터
        nn.AdaptiveAvgPool2d((4, 4)),               # [7]
        nn.Flatten(),                               # [8]

        # [Head] 3개 클래스 분류
        nn.Linear(256, 3)                           # [9]
    )

    # 사전학습된 Backbone 가중치 불러오기
    # Target 이미지로 학습한 모델이 아닌 별도의 source 가중치 사용
    with np.load(
        DATA / "source_backbone.npz",
        allow_pickle=False
    ) as saved:

        state = model.state_dict()

        state.update({
            name: torch.from_numpy(saved[name].copy())
            for name in saved.files
        })

    model.load_state_dict(state)

    # 모든 파라미터 동결
    for p in model.parameters():
        p.requires_grad = False

    # 마지막 Head만 학습 가능하도록 설정
    for p in model[9].parameters():
        p.requires_grad = True

    # Backbone의 BatchNorm Running Mean/Var 고정
    model.eval()

    return model


# ============================================================
# 4. 모델 학습 함수
# ============================================================

def train_model(model, X_train, y_train):
    """
    분류 Head를 1 Epoch 학습합니다.

    오분류를 관찰하기 위한 실습이므로
    최종 학습 모델과 구분해야 합니다.
    """

    # Head 파라미터만 Optimizer에 전달
    optimizer = torch.optim.AdamW(
        model[9].parameters(),
        lr=0.01,
        weight_decay=0.0
    )

    # 다중 클래스 분류용 손실함수
    criterion = nn.CrossEntropyLoss()

    # 1 Epoch 학습
    for epoch in range(1):

        # 이전 Gradient 초기화
        optimizer.zero_grad()

        # 순전파 및 손실 계산
        logits = model(X_train)
        loss = criterion(logits, y_train)

        # 역전파: Head의 Gradient 계산
        loss.backward()

        # Optimizer가 Head 파라미터 갱신
        optimizer.step()

    return model


# ============================================================
# 5. 검증 데이터 예측 함수
# ============================================================

def predict_model(model, X_valid):
    """
    검증 이미지에 대한 클래스별 확률과 예측 라벨을 생성합니다.
    """

    # 학습이 아닌 추론이므로 Gradient 계산 비활성화
    with torch.no_grad():

        # 클래스별 Logit 계산
        logits = model(X_valid)

        # Softmax로 클래스별 확률 계산
        probabilities = logits.softmax(dim=1)

        # 가장 높은 Logit을 가진 클래스를 예측
        predictions = logits.argmax(dim=1)

    return probabilities, predictions


# ============================================================
# 6. 혼동행렬 및 오분류 분석 함수
# ============================================================

def analyze_errors(valid, y_valid, predictions):
    """
    혼동행렬과 클래스별 성능을 출력하고
    실제 오분류 이미지 중 최대 3개를 확인합니다.
    """

    # 혼동행렬 생성
    # 행(Row): 실제 클래스
    # 열(Column): 예측 클래스
    #
    # 대각선 값: 올바르게 분류한 데이터
    # 대각선 밖: 잘못 분류한 데이터
    matrix = confusion_matrix(
        y_valid,
        predictions,
        labels=[0, 1, 2]
    )

    print("\n[혼동행렬]")
    print(matrix)

    # 클래스별 Precision, Recall, F1-score 출력
    print("\n[분류 성능 보고서]")
    print(
        classification_report(
            y_valid,
            predictions,
            labels=[0, 1, 2],
            target_names=valid.classes,
            zero_division=0,
            digits=3
        )
    )

    # 실제 라벨과 예측 라벨이 다른 데이터 인덱스 추출
    errors = (
        (predictions != y_valid)
        .nonzero()
        .flatten()
        .tolist()
    )

    print("\n[오분류 분석]")
    print("오답 개수:", len(errors))

    # 오분류 이미지 중 최대 3개만 출력
    for i in errors[:3]:

        filename = Path(valid.samples[i][0]).name

        actual = valid.classes[y_valid[i]]
        predicted = valid.classes[predictions[i]]

        print(
            filename,
            "실제:", actual,
            "예측:", predicted
        )

    return matrix, errors


# ============================================================
# 7. Main 함수: 전체 실행 흐름 관리
# ============================================================

def main():

    print("\n[START] Day14 CNN 오분류 분석\n")

    # ① 학습 및 검증 데이터 준비
    train, valid, X_train, y_train, X_valid, y_valid = load_data()

    # ② CNN 생성 및 사전학습 가중치 적용
    model = create_model()

    # ③ 분류 Head만 1 Epoch 학습
    model = train_model(model, X_train, y_train)

    # ④ 검증 데이터 예측
    probabilities, predictions = predict_model(
        model,
        X_valid
    )

    # ⑤ 혼동행렬 및 오분류 분석
    matrix, errors = analyze_errors(
        valid,
        y_valid,
        predictions
    )

    print("\n[DONE] 오분류 분석 완료")


# ============================================================
# 8. 프로그램 시작점
# ============================================================

# 직접 실행할 때만 main() 함수 호출
# 다른 파일에서 import하면 자동으로 실행되지 않음
if __name__ == "__main__":
    main()