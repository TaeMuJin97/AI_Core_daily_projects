"""
============================================================================================================
[실습 보고서: 05_attention_mask.py - MultiheadAttention의 Key Padding Mask 적용 및 시각화]
1. 실험 목적: 가변 길이 시퀀스 배치에서 Self-Attention을 수행할 때 key_padding_mask를 통해
              패딩 위치가 문맥 합산(Key/Value)에서 완전히 배제되는지 가중치(weights)와 출력 변화로 검증함.
2. 고정 조건: 입력 Shape [B=2, T=5, E=16], 실제 길이 lengths=[3, 5], num_heads=4, average_attn_weights=False
3. 핵심 구현: 
   - key_padding_mask=mask 전달 전(plain)과 전달 후(masked)의 유효 시점 출력 차이 비교
   - average_attn_weights=False 설정을 통해 Head별 어텐션 가중치 행렬 [B, H, T, T] 추출 및 패딩 열 가중치(0.0) 확인
   - 어텐션 출력 이후 Padded Query 위치를 다시 마스킹하여 실제 길이로 평균 풀링(Masked Mean) 수행
4. 주요 산출물: outputs/mask_or_latent.png (샘플별 유효 시점과 차단된 패딩 시점 시각화 이미지)
============================================================================================================
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from torch import nn

torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# 1. 가변 길이 입력 및 Padding Mask 생성
# 샘플 0은 실제 길이 3 (뒤의 2칸이 패딩), 샘플 1은 실제 길이 5 (패딩 없음)
x = torch.randn(2, 5, 16)
lengths = torch.tensor([3, 5])
mask = torch.arange(5).unsqueeze(0) >= lengths.unsqueeze(1)  # Shape: [2, 5], True가 패딩 위치
x[mask] = 0

attention = nn.MultiheadAttention(16, 4, dropout=0, batch_first=True).eval()

with torch.inference_mode():
    # 마스크 없이 어텐션을 수행하면 패딩 위치(0 벡터)도 Linear 투영 후 Bias 등에 의해 Key로 참조됨
    plain, _ = attention(x, x, x)
    
    # TODO A05: Padding을 key로 보지 않게 bool Mask를 전달한다.
    # nn.MultiheadAttention의 key_padding_mask: [B,T], True가 제외 위치이다.
    # BEGIN A05
    # [핵심 포인트 1: key_padding_mask 전달 및 Head별 가중치 확인]
    # key_padding_mask=mask를 넣으면 True인 패딩 열에 -inf를 더해 Softmax 결과가 정확히 0.0이 됩니다.
    # average_attn_weights=False로 두면 4개 Head를 평균 내지 않은 [B=2, H=4, T=5, T=5] 가중치가 반환됩니다.
    masked, weights = attention(x, x, x, key_padding_mask=mask, average_attn_weights=False)
    # END A05
    
    # [핵심 포인트 2: Padded Query 후처리]
    # key_padding_mask는 '누구를 참고할지(Key)'만 막아주므로, 패딩 위치 자체가 질문(Query)이 되어 나온 출력 행은 0이 아닙니다.
    # 따라서 최종 문맥 벡터로 평균 풀링(Pooling)할 때는 (~mask)를 곱해 패딩 행을 다시 지워주어야 합니다.
    mean = (masked * (~mask).unsqueeze(-1)).sum(1) / lengths.unsqueeze(-1)

print("shape:", tuple(masked.shape), tuple(weights.shape))
# 첫 번째 샘플(0)의 모든 Head(:), 모든 Query(:)에서 패딩 Key 위치(3번, 4번 인덱스)의 가중치 최댓값 확인 -> 0.0
print("막은 key weight 최대:", round(weights[0, :, :, 3:].abs().max().item(), 6))
print("유효 query 출력 변화:", round((plain[0, :3] - masked[0, :3]).abs().max().item(), 6))
print("masked mean:", tuple(mean.shape))

plt.figure(figsize=(6, 3))
plt.imshow(mask.int().numpy(), vmin=0, vmax=1)
plt.xlabel("Time")
plt.ylabel("Sample")
plt.title("Padding mask: 1 = ignored")
plt.xticks(range(5))
plt.yticks(range(2))
plt.tight_layout()
plt.savefig(OUT / "mask_or_latent.png", dpi=120)
plt.close()

"""
==============================================================================================================
[실험 결과 요약 및 진단 보고]
1. 어텐션 가중치 Shape 및 차단 검증:
   - average_attn_weights=False 설정으로 weights Shape는 (2, 4, 5, 5) [Batch, Heads, Query_T, Key_T]가 됨.
   - 샘플 0의 패딩 구간(인덱스 3, 4)에 대한 '막은 key weight 최대' 값이 0.0으로 출력되어 패딩 참조가 완벽히 차단됨을 확인함.
2. x[mask] = 0 만으로 부족한 이유 (유효 query 출력 변화 > 0):
   - 패딩 위치의 입력값을 0으로 채워도 내부 Key/Value 선형 층(nn.Linear)의 편향(bias) 때문에 0이 아닌 벡터가 생성됨.
   - 따라서 반드시 key_padding_mask를 명시적으로 전달해야 유효 시점(0~2번)의 출력이 패딩에 오염되지 않음.
==============================================================================================================
"""