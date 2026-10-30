"""Day5 실습 06 · 열별 전처리와 기준선 연결 · 응용."""
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
from sklearn.dummy import DummyClassifier

def prior_preprocessor():
    """제공: 실습 06 기본필수의 열별 처리기를 재사용합니다."""
    return ColumnTransformer([("num",prior_numeric(),NUM),("cat",prior_categorical(),CAT)],remainder="drop")

def make_model():
    """preprocessing → DummyClassifier(most_frequent)의 미학습 Pipeline 반환.
    단계 이름은 pre, model. 실제 예측 모델의 원리/비교는 다음 수업입니다.
    """
    # 해설 D5-06-A1
    return Pipeline([("pre",prior_preprocessor()),("model",DummyClassifier(strategy="most_frequent"))])

def valid_metrics(y,predictions):
    """valid 예측의 correct,total,accuracy,found_failed,total_failed를 계산합니다.
    X/y가 정렬된 상황에 사용하며 test 데이터는 받지 않습니다.
    """
    # 해설 D5-06-A2
    pred=np.asarray(predictions); actual=y.to_numpy()
    if len(pred)!=len(actual) or len(actual)==0:
        raise ValueError("정답·예측 길이가 다르거나 비어 있습니다.")
    correct=int((pred==actual).sum())
    return {"correct":correct,"total":len(actual),"accuracy":correct/len(actual),
            "found_failed":int(((pred==1)&(actual==1)).sum()),"total_failed":int((actual==1).sum())}

def run():
    tr,va,ytr,yva=load_dev(); model=make_model().fit(tr,ytr)
    pred=model.predict(va); new=new_requests()
    metrics=valid_metrics(yva,pred)
    return {"validation":metrics,"prediction_values":np.unique(pred).tolist(),
            "new_ready_shape":list(model.named_steps["pre"].transform(new).shape),
            "new_predictions":model.predict(new).tolist()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
