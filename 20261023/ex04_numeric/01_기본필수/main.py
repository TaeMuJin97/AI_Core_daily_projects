"""Day5 실습 04 · 결측 대체와 수치형 변환 · 기본필수."""
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

def median_fill(train,valid):
    """train의 열별 중앙값을 학습하고 두 배열을 변환합니다.
    반환: fitted imputer, train_ready, valid_ready. valid에는 transform만 적용합니다.
    """
    # TODO D5-04-B1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-04-B1를 완성하세요.")

def run():
    tr=np.array([[100.],[200.],[np.nan],[900.]])
    va=np.array([[np.nan],[5000.]])
    imp,a,b=median_fill(tr,va)
    Xtr,Xva,_,_=load_dev()
    common,aa,bb=median_fill(Xtr[NUM],Xva[NUM])
    return {"small_median":imp.statistics_.tolist(),"small_train":a.ravel().tolist(),
            "small_valid":b.ravel().tolist(),"common_medians":common.statistics_.tolist(),
            "common_shapes":[list(aa.shape),list(bb.shape)]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
