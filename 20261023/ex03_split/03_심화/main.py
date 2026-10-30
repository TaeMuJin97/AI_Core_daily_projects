"""Day5 실습 03 · 60·20·20 분할과 무결성 검사 · 심화."""
from pathlib import Path
import sys
import argparse
# 제공 코드: 역할 폴더 전체를 유지하면 현재 작업 폴더와 무관하게 실행할 수 있습니다.
ROLE_ROOT = Path(__file__).resolve().parents[2]
if str(ROLE_ROOT) not in sys.path:
    sys.path.insert(0, str(ROLE_ROOT))
from course_support import (DATA, NUM, CAT, FEATURES, FORBIDDEN, read_table,
                            load_raw, load_xy, load_dev, new_requests, emit)
import numpy as np
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit, TimeSeriesSplit

def grouped_indices(groups):
    """E22: 그룹 1/3을 별도 holdout으로 배치하여 dev_idx, holdout_idx를 반환.
    test_size는 행 비율이 아니라 그룹 비율입니다. seed=42, n_splits=1.
    """
    # TODO D5-03-H1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-H1를 완성하세요.")

def time_indices(values):
    """E23: 시간순 입력을 TimeSeriesSplit(n_splits=3)으로 나눈 index 쌍 목록 반환.
    각 fold는 가장 늦은 훈련 index < 가장 이른 검증 index를 만족해야 합니다.
    """
    # TODO D5-03-H2: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-H2를 완성하세요.")

def run():
    groups=np.repeat(["s1","s2","s3","s4","s5","s6"],2)
    dev,holdout=grouped_indices(groups)
    folds=time_indices(np.arange(8).reshape(-1,1))
    return {"group_sizes":[len(dev),len(holdout)],
            "group_overlap":len(set(groups[dev]) & set(groups[holdout])),
            "time_folds":[{"train":a.tolist(),"valid":b.tolist()} for a,b in folds],
            "time_ordered":all(a.max()<b.min() for a,b in folds)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
