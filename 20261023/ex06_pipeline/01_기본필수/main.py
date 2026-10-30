"""Day5 실습 06 · 열별 전처리와 기준선 연결 · 기본필수."""
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
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

def prior_numeric():
    """제공: 앞 단원의 수치형 처리 순서를 재사용합니다."""
    return Pipeline([("imputer",SimpleImputer(strategy="median")),("scaler",StandardScaler())])

def prior_categorical():
    """제공: 앞 단원의 범주형 처리 순서를 재사용합니다."""
    return Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),
        ("encoder",OneHotEncoder(handle_unknown="ignore",sparse_output=False))])

from sklearn.compose import ColumnTransformer

def make_preprocessor():
    """NUM은 prior_numeric(), CAT은 prior_categorical()에 연결합니다.
    경로 이름 num/cat, remainder='drop'인 미학습 ColumnTransformer를 반환합니다.
    """
    # 해설 D5-06-B1
    return ColumnTransformer([("num",prior_numeric(),NUM),
                              ("cat",prior_categorical(),CAT)],remainder="drop")

def run():
    tr,va,_,_=load_dev(); pre=make_preprocessor()
    a=pre.fit_transform(tr); b=pre.transform(va)
    names=pre.get_feature_names_out().tolist()
    ready=pd.DataFrame(b,columns=names,index=va.index)
    return {"train_shape":list(a.shape),"valid_shape":list(b.shape),
            "feature_names":names,"finite":bool(np.isfinite(a).all() and np.isfinite(b).all()),
            "ids_preserved":ready.index.equals(va.index)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
