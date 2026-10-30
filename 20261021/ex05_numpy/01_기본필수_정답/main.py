"""행=요청 3개, 열=Planner/Researcher 2개, 단위=ms인 합성 자료."""
from pathlib import Path
import json
import numpy as np
BASE = Path(__file__).resolve().parent

def make_latency():
    # 해설 ARRAY: [[100,200],[150,250],[200,300]]을 dtype=float인 ndarray로 만드세요.
    return np.array([[100, 200], [150, 250], [200, 300]], dtype=float)

def check_matrix(a):
    """제공된 경계 검사. 비어 있거나 2차원이 아니거나 유한한 수가 아니면 거부합니다."""
    if not isinstance(a, np.ndarray) or a.ndim != 2 or a.size == 0:
        raise ValueError("비어 있지 않은 2차원 ndarray가 필요합니다")
    if not np.isfinite(a).all():
        raise ValueError("유한한 수만 허용합니다")

def basic_stats(a):
    check_matrix(a)
    # 해설 BASIC-STATS: shape·전체 평균·최댓값·초 단위 배열을 Dict에 반환하세요. 원본 a를 바꾸지 마세요.
    return {"shape": list(a.shape), "mean_ms": float(a.mean()),
            "max_ms": float(a.max()), "seconds": (a / 1000).tolist()}

def axis_stats(a):
    check_matrix(a)
    # 해설 AXIS: 역할별/요청별 평균과 200ms 이상인 값·개수를 계산하세요.
    selected = a[a >= 200]
    return {"by_role": a.mean(axis=0).tolist(),
            "by_request": a.mean(axis=1).tolist(),
            "selected_ms": selected.tolist(), "selected_count": int(selected.size)}

def add_offsets(a, by_role):
    check_matrix(a)
    if not isinstance(by_role, np.ndarray) or by_role.ndim != 1 or by_role.shape[0] != a.shape[1]:
        raise ValueError("보정값은 역할 수와 같은 길이의 1차원 배열이어야 합니다")
    # 해설 BROADCAST: 각 요청에 같은 역할별 보정값을 더한 새 배열을 반환하세요.
    return a + by_role

def view_copy_demo():
    # 해설 VIEW-COPY: [10,20,30]의 앞 2개 view를 99로 수정한 뒤 copy를 5로 수정하고 세 결과를 반환하세요.
    a = np.array([10, 20, 30])
    view = a[:2]
    view[0] = 99
    after_view = a.tolist()
    copied = a[:2].copy()
    copied[0] = 5
    return {"after_view": after_view, "after_copy_original": a.tolist(), "copy": copied.tolist()}

def main():
    a = make_latency()
    result = basic_stats(a)

    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    output = BASE / "outputs" / "latency_summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("저장: outputs/latency_summary.json")

if __name__ == "__main__":
    main()
