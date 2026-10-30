"""Day5 실습 04 · 결측 대체와 수치형 변환 · 응용."""
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
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def make_numeric():
    """imputer(median) → scaler(StandardScaler) 순서의 새 Pipeline을 반환.
    이 함수는 객체를 구성할 뿐 fit하지 않습니다.
    """
    # TODO D5-04-A1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-04-A1를 완성하세요.")

def snapshot(pipe):
    """fitted 수치 Pipeline의 대표값·평균·표준편차를 독립 복사한 dict를 반환.
    keys: median, mean, scale. 원본 배열에 대한 참조를 보관하면 비교가 무의미합니다.
    """
    # TODO D5-04-A2: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-04-A2를 완성하세요.")

def run():
    Xtr,Xva,_,_=load_dev(); pipe=make_numeric()
    a=pipe.fit_transform(Xtr[NUM]); before=snapshot(pipe)
    b=pipe.transform(Xva[NUM])
    probe=Xva[NUM].copy(); probe["input_chars"]=1_000_000.
    pipe.transform(probe); after=snapshot(pipe)
    return {"train_shape":list(a.shape),"valid_shape":list(b.shape),
            "finite":bool(np.isfinite(a).all() and np.isfinite(b).all()),
            "train_medians":before["median"].tolist(),
            "state_unchanged":all(np.array_equal(before[k],after[k]) for k in before)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
