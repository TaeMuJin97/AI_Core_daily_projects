"""
======================================================================================================
[실습 보고서: 02_outputs.py - RNN의 Many-to-One vs Many-to-Many 출력 구조 비교]
1. 실험 목적: nn.RNN이 반환하는 전체 시점 출력(output)을 활용하여 시퀀스 전체를 하나로 분류하는
              Many-to-One 구조와 매 시점마다 예측값을 내놓는 Many-to-Many 구조의 텐서 Shape 및 동등성을 확인함.
2. 고정 조건: 입력 Shape [B=4, T=6, F=3], RNN 은닉 크기(H=8, batch_first=True), 분류 Head(8 -> 2)
3. 핵심 구현: 
   - Many-to-One: 마지막 시점의 은닉 상태(output[:, -1], [4, 8])만 선택하여 Head 통과 -> [4, 2]
   - Many-to-Many: 모든 시점의 은닉 상태(output, [4, 6, 8])를 그대로 Head에 통과 -> [4, 6, 2]
4. 주요 산출물: 
   - 콘솔 출력: Many-to-One Shape((4, 2)), Many-to-Many Shape((4, 6, 2)), 마지막 시점 로짓 일치 여부(True)
======================================================================================================
"""

import torch
from torch import nn

torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)

# 1. 입력 데이터 및 모델 레이어 초기화
# 입력 x: 배치 4개, 시퀀스 길이 6, 시점당 특성 3개 -> [4, 6, 3]
x = torch.randn(4, 6, 3)
core = nn.RNN(3, 8, batch_first=True)
head = nn.Linear(8, 2)

# 2. RNN 순전파
# output: 모든 시점의 마지막 층 은닉 상태 -> [B=4, T=6, H=8]
# h: 마지막 시점의 은닉 상태 (batch_first와 무관하게 축 고정) -> [L*D=1, B=4, H=8]
output, h = core(x)

# [패턴 1: Many-to-One (Sequence Classification / 최종 예측)]
# 마지막 시점(-1)의 출력만 슬라이싱하여([4, 8]) 분류기에 입력 -> 결과 Shape: [4, 2]
many_to_one = head(output[:, -1])

# TODO A02: 모든 시점의 hidden을 같은 Linear 층에 넣어 시점별 logits를 만든다.
# Linear는 마지막 차원에 적용되므로 [B,T,H]→[B,T,C]로 작동한다.
# BEGIN A02
# [패턴 2: Many-to-Many (Per-step Tagging / 시점별 상태 예측)]
# PyTorch의 nn.Linear는 3차원 텐서 [B, T, H]가 들어오면 앞의 [B, T]는 배치처럼 취급하고
# 마지막 차원 H(8)를 C(2)로 변환하여 [4, 6, 2] 텐서를 한 번에 반환합니다.
many_to_many = head(output)
# END A02

print("one:", tuple(many_to_one.shape), "many:", tuple(many_to_many.shape))
# [검증: torch.allclose] 부동소수점 오차 범위 내에서 두 텐서의 값이 완전히 일치하는지 확인합니다.
# Many-to-Many 결과의 마지막 시점(many_to_many[:, -1])은 Many-to-One 결과와 정확히 같습니다.
print("마지막 logits 일치:", torch.allclose(many_to_many[:, -1], many_to_one))
print("같은 Head를 시점마다 재사용하며, 시점별 정답은 별도 설계가 필요하다.")

"""
=======================================================================================================
[실험 결과 요약 및 진단 보고]
1. 출력 Shape 비교:
   - Many-to-One: 시점 축(T=6)이 사라지고 샘플당 1개의 예측 벡터만 남아 (4, 2)가 됨.
   - Many-to-Many: 모든 시점 축(T=6)이 보존되어 샘플당 6개의 예측 벡터를 갖는 (4, 6, 2)가 됨.
2. 연산 동등성 확인 (마지막 logits 일치 = True):
   - Linear 층을 모든 시점에 일괄 적용한 뒤 마지막 시점을 뽑은 값(many_to_many[:, -1])과
     마지막 시점 은닉 상태만 먼저 뽑아 Linear 층에 넣은 값(many_to_one)은 수학적으로 100% 동일함.
3. 실무 적용 기준:
   - 문장 감성 분류나 센서 이상 유무 판정처럼 시퀀스 전체에 정답 라벨이 1개인 경우 Many-to-One을 사용하고,
     형태소 태깅이나 시점별 설비 상태 모니터링처럼 매 시점(t)마다 정답 라벨이 존재하는 경우 Many-to-Many를 사용함.
=======================================================================================================
"""