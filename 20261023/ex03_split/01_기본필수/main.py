"""Day5 실습 03 · 60·20·20 분할과 무결성 검사 · 기본필수."""
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

from sklearn.model_selection import train_test_split

def split_xy(X,y,seed=42):
    """같은 호출로 X,y를 두 번 나눕니다.
    반환: {train:(X_train,y_train), valid:(X_valid,y_valid), test:(X_test,y_test)}.
    1차 test_size=0.20, 2차 개발용의 test_size=0.25, 각 단계 stratify를 적용합니다.
    """
    # TODO D5-03-B1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-B1를 완성하세요.")

def check_parts(parts, all_ids):
    """각 부분의 ID 고유성·교집합 없음·전체 포함·X/y index 순서 일치를 검사합니다.
    잘못되면 ValueError, 올바르면 True. 단순 행 수만 맞춰서는 안 됩니다.
    """
    # TODO D5-03-B2: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-B2를 완성하세요.")

def run():
    X,y=load_xy(); parts=split_xy(X,y)
    valid=check_parts(parts,X.index)
    return {"sizes":{k:len(v[0]) for k,v in parts.items()},
            "class_counts":{k:v[1].value_counts().sort_index().to_dict() for k,v in parts.items()},
            "integrity":valid,"unique_ids":len(set().union(*(set(v[0].index) for v in parts.values())))}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
