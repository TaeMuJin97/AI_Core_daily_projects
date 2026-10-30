# 파일 경로를 객체 지향적으로 다루기 위해 pathlib 모듈의 Path 클래스를 불러옵니다.
from pathlib import Path
# CSV 파일 읽기 및 데이터프레임 조작을 위해 pandas 라이브러리를 불러옵니다.
import pandas as pd
# 파이토치(PyTorch) 핵심 라이브러리를 불러옵니다.
import torch
# 신경망 레이어(Linear, ReLU 등)와 손실 함수를 사용하기 위해 torch.nn 모듈을 불러옵니다.
from torch import nn

# CPU 연산 시 사용할 스레드 수를 1개로 제한하여 실행 환경에 따른 연산 순서 차이(재현성 문제)를 방지합니다.
torch.set_num_threads(1)
# 현재 실행 중인 파이썬 스크립트 파일(__file__)의 절대 경로를 구한 뒤, 그 파일이 속한 부모 폴더 경로를 가져옵니다.
base = Path(__file__).resolve().parent
# 부모 폴더 경로(base)에 있는 "points.csv" 파일을 읽어 판다스 DataFrame으로 저장합니다.
df = pd.read_csv(base / "points.csv")
# DataFrame에서 "split" 컬럼 값이 "train"인 행들만 필터링하여 학습 데이터셋으로 분리합니다.
train = df[df["split"] == "train"]
# DataFrame에서 "split" 컬럼 값이 "valid"인 행들만 필터링하여 검증 데이터셋으로 분리합니다.
valid = df[df["split"] == "valid"]
# 학습 데이터의 입력 특성("x1", "x2" 컬럼)을 넘파이 배열(.values)로 추출한 뒤, 신경망 연산을 위해 32비트 실수형(float32) 텐서로 변환합니다.
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
# 학습 데이터의 정답 레이블("label" 컬럼)을 추출하여 CrossEntropyLoss가 요구하는 64비트 정수형(long / int64) 텐서로 변환합니다.
y_train = torch.tensor(train["label"].values, dtype=torch.long)
# 검증 데이터의 입력 특성("x1", "x2" 컬럼)을 32비트 실수형(float32) 텐서로 변환합니다.
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32)
# 검증 데이터의 정답 레이블("label" 컬럼)을 64비트 정수형(long) 텐서로 변환합니다.
y_valid = torch.tensor(valid["label"].values, dtype=torch.long)
# test 4건은 읽은 표에만 있으며 학습/평가 Tensor로 만들지 않습니다.

# 다중/이진 분류를 위한 교차 엔트로피 손실 함수(CrossEntropyLoss) 객체를 생성합니다. (내부적으로 Softmax와 NLLLoss를 결합하여 계산합니다.)
loss_fn = nn.CrossEntropyLoss()
# 비교할 두 가지 옵티마이저 이름("SGD", "AdamW")을 순회하며 동일한 조건에서 각각 학습 및 평가를 진행합니다.
for name in ["SGD", "AdamW"]:
    # 후보마다 같은 초기 가중치에서 다시 시작합니다. 앞 모델을 이어 학습하지 않습니다.
    # 난수 시드(seed)를 42로 고정하여 두 옵티마이저가 완전히 동일한 초기 가중치 상태에서 학습을 시작하도록 보장합니다.
    torch.manual_seed(42)
    # 2차원 입력 -> 은닉층(8개 뉴런) -> ReLU 활성화 함수 -> 출력층(2개 클래스 로짓)으로 구성된 다층 퍼셉트론(MLP) 모델을 생성합니다.
    model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2))
    # 현재 순회 중인 옵티마이저 이름이 "SGD"인 경우의 분기입니다.
    if name == "SGD":
        # SGD의 학습할 파라미터는 model.parameters()입니다. lr=0.01, momentum=0.0으로 만드세요.
        # 학습률은 기본값에 기대지 않고 명시하며, 두 Optimizer 모두 weight_decay=0.0으로 비교합니다.
        # >>> B01
        # TODO B01: 위 요구사항에 맞게 이 블록만 완성합니다.
        # 확률적 경사 하강법(SGD) 옵티마이저를 생성합니다. 모델의 모든 가중치/편향을 등록하고, 학습률(lr=0.01), 모멘텀 없음(momentum=0.0), 가중치 감쇠 없음(weight_decay=0.0)으로 설정합니다.
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.0, weight_decay=0.0)
        # <<< B01
    # 현재 순회 중인 옵티마이저 이름이 "SGD"가 아닌 경우("AdamW"인 경우)의 분기입니다.
    else:
        # AdamW를 같은 lr=0.01로 만드세요. weight_decay=0.0을 반드시 적으세요.
        # 이번에는 감쇠 효과가 아닌 갱신 규칙을 비교합니다. 이 공통 lr이 두 알고리즘의 최적 lr이라는 뜻은 아닙니다.
        # >>> B02
        # TODO B02: 위 요구사항에 맞게 이 블록만 완성합니다.
        # 적응적 모멘트 추정(AdamW) 옵티마이저를 생성합니다. 순수하게 파라미터 갱신 규칙의 차이만 비교하기 위해 동일한 학습률(lr=0.01)과 가중치 감쇠 없음(weight_decay=0.0)을 명시합니다.
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=0.0)
        # <<< B02
    # 전체 학습 데이터셋(X_train, y_train)에 대해 총 20번(20 에포크) 반복 학습을 수행합니다.
    for epoch in range(20):
        # 모델을 학습 모드(train mode)로 전환합니다. (Dropout이나 BatchNorm 등이 있을 때 학습 동작을 활성화하는 표준 관례입니다.)
        model.train()
        # 이전 에포크(step)에서 계산되어 파라미터에 누적되어 있는 기울기(gradient)를 0으로 초기화합니다.
        optimizer.zero_grad()
        # 학습 데이터 X_train을 모델에 통과시켜 예측값(로짓)을 얻고, 정답 y_train과 비교하여 현재 에포크의 손실(loss)을 계산합니다. (순전파)
        loss = loss_fn(model(X_train), y_train)
        # 손실(loss)에 대해 모델의 각 파라미터별 기울기(gradient)를 역전파(Backpropagation) 알고리즘으로 계산합니다.
        loss.backward()
        # 계산된 기울기를 바탕으로 옵티마이저(SGD 또는 AdamW)의 갱신 규칙에 따라 모델의 파라미터(가중치와 편향)를 업데이트합니다.
        optimizer.step()
    # 20 에포크 학습이 끝난 후, 평가를 위해 모델을 평가 모드(evaluation mode)로 전환합니다.
    model.eval()
    # 평가 시에는 기울기 계산이 필요 없으므로, 메모리 사용량을 줄이고 연산 속도를 높이기 위해 그래디언트 추적을 비활성화합니다.
    with torch.no_grad():
        # 검증 데이터(X_valid)에 대한 예측값과 정답(y_valid) 사이의 손실을 계산한 뒤, .item()을 통해 텐서에서 파이썬 스칼라 숫자 값만 추출합니다.
        valid_loss = loss_fn(model(X_valid), y_valid).item()
    # 사용한 옵티마이저 이름과 20 에포크 학습 후의 검증 손실(소수점 6자리까지 반올림)을 화면에 출력합니다.
    print(name, "20 epochs / valid loss:", round(valid_loss, 6))

""" 주요 추가된 설명 내용

  • 데이터 로드 및 텐서 변환 (01_optimizer.py:1-28): Path를 이용한 파일 경로 탐색, train/valid
  데이터 분리, 입력 특성(float32)과 정답 레이블(long)의 자료형 지정 이유
  • 모델 및 옵티마이저 초기화 (01_optimizer.py:30-57): nn.CrossEntropyLoss의 역할, 공정한 비교를
  위한 torch.manual_seed(42) 고정, SGD와 AdamW의 하이퍼파라미터(lr, momentum, weight_decay) 설정
  의미
  • 학습 및 평가 루프 (01_optimizer.py:58-78): model.train(), zero_grad(),
  순전파/역전파(backward()), 파라미터 갱신(step()), 그리고 model.eval() 및 torch.no_grad()를 통한
  검증 손실 계산 과정"""