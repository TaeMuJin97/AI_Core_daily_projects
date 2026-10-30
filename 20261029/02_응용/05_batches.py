"""실습 05: 마지막 작은 batch를 버리지 않고 자료를 모두 읽습니다."""
from pathlib import Path
import csv
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

# - 이진 분류 레이블(y)은 CrossEntropyLoss 요구 조건에 맞추어 정수형(torch.long)으로 선언
X = torch.arange(20, dtype=torch.float32).reshape(10, 2) / 10
y = torch.tensor([0, 0, 0, 0, 0, 1, 1, 1, 1, 1], dtype=torch.long)

dataset = TensorDataset(X, y)
# dataset을 batch_size=4, shuffle=False, drop_last=False로 공급하세요.
# 정상 데이터 10건이 4·4·2로 나뉘어야 합니다. num_workers=0을 유지합니다.
# >>> A05
# TODO A05: 위 요구사항을 읽고 이 블록을 완성하세요.

# [핵심] DataLoader 설정:
# - batch_size=4: 데이터를 4개씩 묶음
# - drop_last=False: 10건을 4개씩 묶을 때 남는 마지막 자투리 2건을 버리지 않고 온전히 유지 (4 -> 4 -> 2)
# - shuffle=False: 순서 유지
# - num_workers=0: 메인 프로세스에서 단일 스레드로 로딩 (윈도우 환경 안전성 확보)
loader = DataLoader(dataset, batch_size=4, shuffle=False, drop_last=False, num_workers=0)
# <<< A05

# 미니배치 순회 및 크기 확인
sizes = []
for index, (xb, yb) in enumerate(loader, 1):

    # 각 미니배치별 xb shape: (배치크기, 2), yb shape: (배치크기,)
    sizes.append([index, len(yb)])
    print(index, tuple(xb.shape), tuple(yb.shape))

print("합계:", sum(n for _, n in sizes))

# [4] CrossEntropyLoss 동작 검증
# - 2개의 클래스(0, 1)에 대해 모델이 출력한 raw logit 점수
# - nn.CrossEntropyLoss는 내부적으로 Softmax 연산을 수행하므로 정규화되지 않은 logits를 그대로 입력
logits = torch.tensor([[2., 0.], [0., 2.]])
print("예시 CE:", round(nn.CrossEntropyLoss()(logits, torch.tensor([0, 1])).item(), 6))

# 폴더 생성
out = Path(__file__).resolve().parent / "outputs"
out.mkdir(exist_ok=True)
with (out / "batch_sizes.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f); 
    writer.writerow(["batch", "samples"]); 
    writer.writerows(sizes)

# 추가 A09: 배치 크기가 다를 때 평균 loss를 합치는 방법입니다.
# 입력: 평균 손실 [0.1, 0.2, 0.9], 각 배치의 표본 수 [4, 4, 2].
# 요구: loss × 실제 표본 수의 합을 전체 표본 수로 나누세요.
# 금지: 배치 평균 세 개를 단순 평균하거나 마지막 배치를 4건으로 계산하지 않습니다.
# 완료: weighted_loss=0.3. 잘못된 단순 평균 0.4와 차이를 설명합니다.
loss_means = [0.1, 0.2, 0.9]
sample_counts = [4, 4, 2]

# >>> A09
# TODO A09: 배치 크기까지 반영한 평균을 계산하세요.
# - 각 배치의 loss_mean은 해당 배치의 '표본당 평균'이므로, 배치 표본 수를 곱해 '총 손실'을 복원한 후 전체 표본 수로 나눔
# - (0.1*4 + 0.2*4 + 0.9*2) / (4 + 4 + 2) = (0.4 + 0.8 + 1.8) / 10 = 3.0 / 10 = 0.3
weighted_loss = sum(loss * n for loss, n in zip(loss_means, sample_counts)) / sum(sample_counts)
# <<< A09

print("샘플 가중 loss:", round(weighted_loss, 6))
print("배치 단순 평균:", round(sum(loss_means) / len(loss_means), 6))
