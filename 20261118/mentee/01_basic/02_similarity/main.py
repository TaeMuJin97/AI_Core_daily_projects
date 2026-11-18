"""
==============================================================================
[실습 보고서: Day 23 실습 02 - Vector · Similarity · Distance 수학 연산 검증 (main.py)]
1. 실험 목적:
   - Embedding 벡터 간 가까움을 측정하는 3대 핵심 척도(Dot Product, Cosine Similarity, L2 Distance)와
     pgvector 정렬 기준인 Cosine Distance(1 - Cosine Similarity)의 수치 및 정렬 방향을 직접 검증함.
2. 핵심 아키텍처 개념:
   - 내적(Dot Product)과 벡터 길이(Norm)의 영향 (D23-02-B01):
     내적은 방향뿐 아니라 벡터의 크기(norm)에도 비례하므로, 정규화되지 않은 벡터에서는 길이가 긴 후보가
     더 큰 점수를 받을 수 있음. (길이를 1로 정규화하면 내적과 Cosine Similarity가 일치함)
   - Cosine Similarity 및 영벡터(Zero-vector) 방어 (D23-02-B02):
     두 벡터의 사잇각 코사인 값을 계산하되, 길이가 0인 영벡터가 입력되면 분모가 0이 되어 수학적으로
     정의되지 않으므로 0점으로 조용히 통과시키지 않고 ValueError를 발생시켜 차단함.
   - L2 Distance (Euclidean Distance) (D23-02-B03):
     두 벡터 끝점 사이의 직선거리로, 값이 작을수록(ASC) 가까운 후보를 의미함.
==============================================================================
"""
"""Day23 실습 02 · Vector·Similarity·Distance (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
import numpy as np
from day23kit.mathops import cosine_distance
from day23kit.io import save_result


# BEGIN D23-02-B01
def dot(a, b):
    """
    TODO D23-02-B01 · dot
        같은 위치의 숫자를 곱해 합산하는 내적을 구현하세요.
        예: (1,0)·(0.8,0.6)=0.8. 입력 NumPy 배열 2개, 출력 float.
    """
    # [핵심 포인트 1: NumPy 내적 연산 및 순수 Python float 변환]
    # - np.dot(a, b)는 numpy.float64 스칼라를 반환할 수 있으므로 JSON 직렬화 안전성을 위해 float()로 감쌉니다.
    arr_a = np.asarray(a, dtype=np.float64)
    arr_b = np.asarray(b, dtype=np.float64)
    return float(np.dot(arr_a, arr_b))
# END D23-02-B01


# BEGIN D23-02-B02
def cosine(a, b):
    """
    TODO D23-02-B02 · cosine
        내적을 두 벡터 길이의 곱으로 나누어 Cosine similarity를 구하세요.
        q=(1,0), A=(0.8,0.6)라면 0.8입니다.
        입력: NumPy 배열 2개. 출력: float. 영벡터는 무조건 거부합니다.
    """
    # [핵심 포인트 2: 벡터 길이(L2 Norm) 계산 및 영벡터(Zero-vector) 차단]
    # - 영벡터는 방향이 없으며 분모(length_a * length_b)가 0이 되므로 반드시 ValueError로 거부합니다.
    arr_a = np.asarray(a, dtype=np.float64)
    arr_b = np.asarray(b, dtype=np.float64)
    length_a = float(np.linalg.norm(arr_a))
    length_b = float(np.linalg.norm(arr_b))
    if length_a <= 1e-12 or length_b <= 1e-12:
        raise ValueError("영벡터(norm=0)는 Cosine similarity를 계산할 수 없습니다.")
    return float(dot(arr_a, arr_b) / (length_a * length_b))
# END D23-02-B02


# BEGIN D23-02-B03
def l2(a, b):
    """
    TODO D23-02-B03 · l2
        두 벡터의 좌표 차이로 L2 거리를 구하세요. 출력 float.
        q=(1,0), A=(0.8,0.6) → sqrt(0.4) ≈ 0.6325.
    """
    # [핵심 포인트 3: 유클리드 직선거리(L2 Distance) 계산]
    # - 두 벡터의 차(arr_a - arr_b)의 L2 노름을 계산하여 직선 거리를 구합니다.
    arr_a = np.asarray(a, dtype=np.float64)
    arr_b = np.asarray(b, dtype=np.float64)
    return float(np.linalg.norm(arr_a - arr_b))
# END D23-02-B03


def run(mode, level, args):
    q = np.array([1.0, 0.0])
    a = np.array([0.8, 0.6])
    u = np.array([1.0, 0.0])
    v = np.array([10.0, 10.0])
    result = dict(
        exercise=2,
        level=level,
        source_mode="local_math",
        dot=round(dot(q, a), 6),
        cosine=round(cosine(q, a), 6),
        l2=round(l2(q, a), 6),
        cosine_distance=round(1 - cosine(q, a), 6),
    )
    if level >= 2:
        result["normalized_v"] = normalize(v).round(6).tolist()
        result["rankings"] = rank_dot_vs_cosine(q, {"U": u, "V": v})
    if level >= 3:
        result["validated"] = validate_pair(q, a)
        errors = {}
        for label, x, y in [
            ("dimension_mismatch", q, np.array([1.0, 0.0, 2.0])),
            ("nonfinite", q, np.array([np.nan, 1.0])),
            ("zero_vector", q, np.array([0.0, 0.0])),
        ]:
            try:
                validate_pair(x, y)
            except ValueError as e:
                errors[label] = str(e)
        result["invalid_inputs"] = errors
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 02 · Vector·Similarity·Distance"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_02.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()