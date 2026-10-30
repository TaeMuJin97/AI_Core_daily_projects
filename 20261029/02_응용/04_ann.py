"""실습 04: 은닉 너비에 따라 파라미터 수가 변합니다. 학습 성능 비교는 아닙니다."""
import torch
from torch import nn

torch.manual_seed(42)
X = torch.ones(4, 2)
for hidden in [4, 8, 16]:

    # hidden 값을 사용해 입력 2개 → 은닉 hidden개 → 출력 2개를 연결하세요.
    # 은닉층 뒤에 ReLU를 넣고 마지막에 softmax는 넣지 않습니다.
    # >>> A04
    # TODO A04: 위 요구사항을 읽고 이 블록을 완성하세요.
    # 선형 층(nn.Linear)들이 하나의 선형 층으로 병합(붕괴)되지 않도록 중간에 활성화 함수(nn.ReLU())를 넣어주는 것
    model = nn.Sequential(
        nn.Linear(2, hidden),  # 첫 번째 Linear: 입력 2개 → 출력 hidden개
        nn.ReLU(),            # 활성화 함수
        nn.Linear(hidden, 2)   # 두 번째 Linear: 입력 hidden개 → 출력 2개
    )
    # <<< A04
    
    logits = model(X)
    count = sum(p.numel() for p in model.parameters())
    print("은닉:", hidden, "출력:", tuple(logits.shape), "파라미터:", count)
