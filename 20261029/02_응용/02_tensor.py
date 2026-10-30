"""실습 02: reshape와 broadcasting을 확인합니다."""
import torch

# 원소 6개를 2행 3열로 바꾸어 matrix에 저장하세요.
a = torch.arange(6, dtype=torch.float32)


# >>> A02
# TODO A02: 위 요구사항을 읽고 이 블록을 완성하세요.
matrix = a.reshape(2, 3) # 2행 3열
# <<< A02

# 아래 bias는 각 열에 더해집니다.
bias = torch.tensor([10., 20., 30.])
result = matrix + bias

print("변환 전:", tuple(a.shape))
print("행렬:", tuple(matrix.shape), matrix.tolist())
print("보정 후:", tuple(result.shape), result.tolist())

# 텐서의 단독 장치(Device) 이동 및 CPU 반환
# - 모델과의 연산이 아니라, '텐서 연산 결과(result)'를 GPU/CPU로 옮기는 기초 문법입니다.
# - CUDA가 사용 가능하면 'cuda:0'(GPU VRAM), 불가능하면 'cpu'(RAM)로 타겟 장치 결정
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# .to(device)로 텐서를 해당 장치로 복사·할당
moved = result.to(device)

print("이동 장치:", moved.device)

# .cpu(): GPU에 있는 텐서를 다시 CPU 메모리로 가져와서 안전하게 파이썬 리스트로 변환
print("CPU에서 확인:", moved.cpu().tolist())
