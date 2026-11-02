"""
==============================================================================
[실습 보고서: 01_mask.py - 가변 길이 Sequence Padding 및 Mask 기반 유효 시점 평균 계산]
1. 실험 목적: 길이가 서로 다른 시퀀스(길이 4, 2, 5)를 하나의 배치(Batch)로 묶기 위해 Padding을 적용하고,
              채워진 0(Padding)이 통계량을 왜곡하지 않도록 Mask와 실제 길이(lengths)를 활용해 정확한 평균을 산출함.
2. 고정 조건: 입력 시퀀스 3개(길이 4, 2, 5 / Feature 수 3), batch_first=True, 패딩 값 0.0
3. 핵심 구현: 
   - pad_sequence를 통해 [3, 5, 3] 규격의 배치 텐서 생성
   - 브로드캐스팅 비교 연산으로 [3, 5] 크기의 불리언 Padding Mask 생성 (True: 패딩, False: 실제 시점)
   - 유효 시점 마스크(~mask)만 합산한 뒤 최대 길이(5)가 아닌 각 샘플의 실제 길이(lengths)로 나누어 평균 계산
4. 주요 산출물: 
   - 콘솔 출력: Padding mask 불리언 텐서([3, 5]) 및 샘플별 실제 값 평균 텐서([3, 3])
   - 파일 저장: outputs/padding_mask.csv (패딩 위치를 0과 1로 기록한 마스크 표)
==============================================================================
"""

from pathlib import Path
import pandas as pd
import torch
from torch.nn.utils.rnn import pad_sequence

torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# 1. 가변 길이 시퀀스 데이터 준비
# 샘플 0: 길이 4 (모든 원소 1.0), 샘플 1: 길이 2 (모든 원소 2.0), 샘플 2: 길이 5 (모든 원소 3.0)
sequences = [torch.ones(4, 3), torch.ones(2, 3) * 2, torch.ones(5, 3) * 3]
lengths = torch.tensor([4, 2, 5])

# [핵심 포인트 1: pad_sequence를 통한 배치 구성]
# 배치 내 최대 길이(T=5)에 맞춰 짧은 시퀀스 뒷부분을 0.0으로 채워 [B=3, T=5, F=3] 텐서로 만듭니다.
padded = pad_sequence(sequences, batch_first=True)

# [핵심 포인트 2: 브로드캐스팅을 활용한 Padding Mask 생성]
# torch.arange(5).unsqueeze(0) -> Shape: [1, 5] (시점 인덱스 0, 1, 2, 3, 4)
# lengths.unsqueeze(1)         -> Shape: [3, 1] (각 샘플의 실제 길이 4, 2, 5)
# 시점 인덱스가 실제 길이보다 크거나 같은 위치(>=)는 패딩이므로 True가 됩니다. (결과 Shape: [3, 5])
mask = torch.arange(padded.size(1)).unsqueeze(0) >= lengths.unsqueeze(1)

# TODO A01: Padding이 아닌 실제 시점만 합산하고 각 자료의 실제 길이로 나눈다.
# mask=True는 Padding이다. 0도 정상 관측값일 수 있으므로 값이 0인지로 판정하지 않는다.
# BEGIN A01
# [핵심 포인트 3: Masked Mean Pooling]
# 단순 padded.mean(dim=1)을 쓰면 패딩된 0까지 합산한 뒤 무조건 5(최대 길이)로 나누어 평균이 작아집니다.
# 따라서 ~mask로 실제 시점(True)만 남기고 [3, 5, 1]로 차원을 늘려 곱한 뒤, 실제 길이(lengths)로 나눕니다.
valid = (~mask).unsqueeze(-1)
mean = (padded * valid).sum(dim=1) / lengths.unsqueeze(1)
# END A01

print("Padding mask:\n", mask)
print("실제 값 평균:\n", mean)
pd.DataFrame(mask.int().numpy()).to_csv(OUT / "padding_mask.csv", index=False)

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 단순 평균(padded.mean(dim=1)) 사용 시 발생하는 오류:
   - 두 번째 샘플(실제 길이 2, 원소 값 2.0)의 경우 뒷부분 3개 시점이 0.0으로 패딩됨.
   - 단순 평균을 내면 (2 + 2 + 0 + 0 + 0) / 5 = 0.8이 되어 원래 값(2.0)이 심각하게 왜곡됨.
2. Mask 기반 평균 계산 결과:
   - 실제 시점만 합산하고 실제 길이(4, 2, 5)로 각각 나눔으로써 [1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]의
     정확한 원본 특성 평균이 복원됨을 확인함.
3. 값 기반 판정(padded != 0) 대신 길이 기반 Mask를 쓰는 이유:
   - 센서나 정규화된 데이터에서는 실제 정상 관측값 자체가 0.0인 경우가 흔하므로, 반드시 lengths 기반의 위치 마스크로 구분해야 함.
==============================================================================
"""