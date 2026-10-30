"""Day5 실습 04 · 결측 대체와 수치형 변환 · 심화."""
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

from sklearn.impute import SimpleImputer

def preserve_empty(train,valid):
    """수치형 전체 결측 열을 유지하는 명시적 정책을 구현합니다.
    median, keep_empty_features=True로 학습한 객체와 두 변환 배열을 반환합니다.
    전체 결측 열의 0은 관측된 중앙값이 아니라 열 보존용 대체값입니다.
    """
    # TODO D5-04-H1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-04-H1를 완성하세요.")

def run():
    train=np.array([[np.nan,1.],[np.nan,3.]])
    valid=np.array([[np.nan,np.nan],[5.,9.]])
    imp,a,b=preserve_empty(train,valid)
    return {"train_shape":list(a.shape),"train_ready":a.tolist(),
            "valid_ready":b.tolist(),"statistics":imp.statistics_.tolist()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
