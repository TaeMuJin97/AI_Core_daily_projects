"""
==============================================================================
[실습 보고서: 06_seed_augmentation.py - 로컬 난수 생성기(Seed) 기반 재현 가능한 데이터 증강 파이프라인]
1. 실험 목적: 독립적인 로컬 난수 생성기(np.random.default_rng)를 사용하여 좌우 반전(Flip)과 밝기 변화(Beta)를
              확률적으로 적용하되, 동일한 Seed 입력 시 100% 동일한 증강 이미지가 재현되는지 검증함.
2. 고정 조건: 입력 이미지(data/scene.png), 난수 시드(seed=42), 반전 확률(0.5), 밝기 조절 범위([-25, 25])
3. 핵심 구현: 
   - np.random.default_rng(seed)로 전역 상태를 오염시키지 않는 로컬 RNG 생성
   - uint8 오버플로우/언더플로우 방지를 위해 float32 변환 -> beta 가산 -> [0, 255] clip -> uint8 복원
   - cv2.hconcat을 활용해 [원본, 1차 증강, 2차 증강] 이미지를 가로로 나란히 이어 붙여 시각적 비교 저장
4. 주요 산출물: 
   - outputs/p06_comparison.png (원본 및 동일 시드 증강 결과 2장을 가로 결합한 비교 이미지)
   - outputs/p06_settings.json (실제 적용된 seed, flip 여부, beta 값 메타데이터 기록)
==============================================================================
"""

import json
import os
from pathlib import Path
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)
Path("outputs").mkdir(exist_ok=True)


def augment(image, seed):
    """로컬 난수로 밝기·좌우반전을 결정합니다. 입력 배열은 변경하지 않습니다."""
    # [핵심 포인트 1: 로컬 난수 생성기(default_rng)를 통한 완벽한 재현성 확보]
    # 전역 np.random.seed() 대신 함수 내부의 독립된 Generator 객체를 사용하여
    # 외부 코드의 난수 호출 순서에 영향을 받지 않고 항상 같은 seed에서 같은 결정을 내립니다.
    rng = np.random.default_rng(seed)
    flip = bool(rng.random() < 0.5)
    beta = int(rng.integers(-25, 26))  # -25 이상 26 미만(즉, -25 ~ 25)의 정수 1개 추출
    
    # 원본 배열 보호를 위해 복사본 생성
    result = image.copy()
    if flip:
        # flipCode=1은 좌우 반전(Horizontal Flip)을 의미합니다.
        result = cv2.flip(result, 1)
        
    # >>> TODO A06
    # float32에서 beta를 더하고 [0,255]로 clip한 뒤 uint8로 돌리세요. uint8 상태로 직접 더하지 않습니다.
    # [핵심 포인트 2: 안전한 화소 밝기 조절 (Saturation Arithmetic 직접 구현)]
    # uint8에서 250 + 20을 하면 270이 아니라 14로 순환(Overflow)하여 하얀 부분이 검게 깨집니다.
    # 따라서 float32로 형변환 후 beta를 더하고, np.clip으로 0 미만은 0, 255 초과는 255로 고정한 뒤 uint8로 복원합니다.
    result = np.clip(result.astype(np.float32) + beta, 0, 255).astype(np.uint8)
    # <<< TODO A06
    
    return result, {"seed": seed, "flip": flip, "beta": beta}


# 1. 원본 이미지 로드 및 동일 시드(42)로 2회 반복 증강 수행
image = cv2.imread("data/scene.png")
first, settings = augment(image, 42)
second, _ = augment(image, 42)

# [새 함수: cv2.hconcat([img1, img2, ...])]
# 높이와 채널 수가 같은 여러 이미지 배열을 가로(Horizontal) 방향으로 나란히 이어 붙여 한 장의 이미지로 만듭니다.
cv2.imwrite("outputs/p06_comparison.png", cv2.hconcat([image, first, second]))

# 2. 적용된 증강 파라미터를 JSON 파일로 기록하여 실험 추적성 확보
Path("outputs/p06_settings.json").write_text(
    json.dumps(settings, indent=2), encoding="utf-8"
)

# [새 함수: np.array_equal(a, b)]
# 두 NumPy 배열의 Shape와 모든 픽셀 원소 값이 단 하나의 오차도 없이 100% 똑같은지 검사하여 bool을 반환합니다.
print("같은 seed 결과 일치:", np.array_equal(first, second))
print("설정:", settings)

"""
==============================================================================
[실험 결과 요약 및 진단 보고]
1. 결정론적 재현성(Deterministic Reproducibility) 확인:
   - 동일한 seed=42를 전달한 first와 second 배열에 대해 np.array_equal 결과가 True로 출력됨.
   - 이는 멀티워커 데이터 로더나 디버깅 환경에서 특정 증강 샘플을 완벽히 재현할 수 있음을 뜻함.
2. 증강 설정 기록(p06_settings.json)의 중요성:
   - 무작위 증강을 적용하더라도 사용된 시드와 실제 뽑힌 파라미터(flip, beta)를 JSON으로 남겨두면,
     추후 모델 성능 변화나 이상 샘플 발생 시 원인을 정확히 역추적할 수 있음.
==============================================================================
"""