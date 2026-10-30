"""실습 03: 매번 새로운 그래프를 만들고 gradient를 비웁니다.
    w를목표값4에가깝게10회갱신한다.
    no_grad 갱신과 gradient 초기화를 연결한다."""
from pathlib import Path
import csv
import torch

# [1] 파라미터 초기화
# - w: 가중치
# - requires_grad=True: PyTorch에게 "이 텐서가 거쳐가는 모든 계산 과정을 그래프로 추적해줘(미분할 거야)"라고 선언
w = torch.tensor(0.0, requires_grad=True)

# lr(Learning Rate, 학습률): 기울기(경사) 방향으로 한 번에 얼만큼 이동할지 결정하는 보폭 크기
lr = 0.1
history = []

for step in range(1, 11): # 1 ~ 10회 반복 (10번의 경사하강법 스텝 수행)
    # [2] 손실(Loss) 계산 및 연산 그래프(Computation Graph) 자동 생성
    # - 목표값(4.0)과의 오차 제곱을 구합니다. (MSE 손실 형태)
    # - 이 줄이 실행될 때 w로부터 loss까지 이어지는 계산 그래프가 메모리에 동적으로 그려집니다.
    loss = (w - 4.0) ** 2

    # [3] 역전파(Backpropagation): 연쇄 법칙(Chain Rule)으로 기울기 계산
    # - 수학적 미분: d(loss)/dw = 2 * (w - 4.0)
    # - step 1일 때: 2 * (0.0 - 4.0) = -8.0
    # - 계산된 미분값(-8.0)이 w의 .grad 속성에 자동으로 저장됩니다 (w.grad = -8.0).
    loss.backward()


    with torch.no_grad():
        # w에서 학습률 × 현재 기울기를 빼세요.
        # 여기는 no_grad 블록 안입니다. 새 값으로 Tensor 객체를 교체하지 말고 w를 직접 갱신하세요.
        # >>> A03
        # TODO A03: 위 요구사항을 읽고 이 블록을 완성하세요.
        w -= (lr * w.grad)
        # w = w - lr * w.grad
        # - w = w - lr * w.grad 를 쓰면 새로운 텐서 객체가 생성되어 기존 leaf 파라미터 연결이 끊어집니다.
        # - 반드시 제자리 수정 연산(In-place)인 `-=`를 사용해야 기존 파라미터 메모리 주소에서 값만 깔끔하게 바뀝니다.
        # <<< A03

# [5] 기울기 초기화 (Zeroing Gradients)
    # - PyTorch는 backward() 호출 시 기울기를 덮어쓰지 않고 기존 w.grad에 '누적(+=)'합니다.
    # - 따라서 다음 스텝에서 새 기울기만 온전히 쓰려면 반드시 .zero_()로 0으로 비워주어야 합니다.
    # - 함수 끝에 밑줄(_)이 붙은 메서드는 원본 데이터를 직접 수정하는 In-place 연산입니다.
    w.grad.zero_()

    # [6] 기록 아카이빙
    # - w.item(): 텐서 안의 숫자 1개를 순수 파이썬 float 타입으로 추출합니다.
    # - w.detach(): 계산 그래프 추적을 완전히 끊어낸 복제 텐서 뷰를 만들어 평가용으로 안전하게 오차를 계산합니다.
    # 아래 loss는 갱신한 w에서 다시 계산한 값입니다.
    history.append([step, w.item(), (w.detach() - 4.0).square().item()])
for step, value, loss_after in history:
    print(step, round(value, 6), round(loss_after, 6))
out = Path(__file__).resolve().parent / "outputs"
out.mkdir(exist_ok=True)
with (out / "gd_history.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f); writer.writerow(["step", "w_after", "loss_after"]); writer.writerows(history)
