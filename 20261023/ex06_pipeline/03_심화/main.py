"""Day5 실습 06 · 열별 전처리와 기준선 연결 · 심화."""
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

def prior_model():
    """제공: 실습 06 응용의 기준선을 재사용합니다."""
    return Pipeline([("pre",prior_preprocessor()),("model",DummyClassifier(strategy="most_frequent"))])

def validate_features(frame,extra="error"):
    """새 요청의 입력 계약을 검사하고 FEATURES 순서의 복사본을 반환합니다.
    누락·중복 열, forbidden 열은 항상 ValueError. extra='error'면 나머지 추가 열도 오류.
    extra='drop'은 note 같은 일반 추가 열만 명시적으로 제외하며 forbidden은 여전히 오류입니다.
    새로운 범주 값은 허용하되 필수 열 누락과 혼동하지 않습니다.
    """
    # 해설 D5-06-H1
    if extra not in {"error","drop"}:
        raise ValueError("extra 정책은 error/drop 중 하나입니다.")
    if not frame.columns.is_unique:
        raise ValueError("중복 열 이름")
    missing=set(FEATURES)-set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    leaked=FORBIDDEN & set(frame.columns)
    if leaked:
        raise ValueError(f"forbidden columns: {sorted(leaked)}")
    extra_cols=set(frame.columns)-set(FEATURES)
    if extra_cols and extra=="error":
        raise ValueError(f"extra columns: {sorted(extra_cols)}")
    return frame[FEATURES].copy()

def check_feature_names(names):
    """출력 특성명이 고유하고 금지 입력에서 온 열이 없으면 True, 아니면 ValueError.
    num__ / cat__ 뒤 이름이 금지 이름 자체 또는 금지명+'_'로 시작하면 거부합니다.
    """
    # 해설 D5-06-H2
    if len(names)!=len(set(names)):
        raise ValueError("중복 출력 특성명")
    for name in names:
        base=name.split("__",1)[-1]
        if any(base==bad or base.startswith(bad+"_") for bad in FORBIDDEN):
            raise ValueError(f"금지 출력 특성: {name}")
    return True

def run():
    tr,va,ytr,_=load_dev(); model=prior_model().fit(tr,ytr)
    names=model.named_steps["pre"].get_feature_names_out().tolist()
    check_feature_names(names)
    new=validate_features(new_requests())
    reordered=validate_features(new[list(reversed(FEATURES))])
    handled={}
    for label,bad in {"missing":new.drop(columns="priority"),
                      "extra":new.assign(note="memo"),"forbidden":new.assign(status="ok")}.items():
        try: validate_features(bad)
        except ValueError: handled[label]=True
        else: handled[label]=False
    return {"names_ok":True,"ordered_columns":reordered.columns.tolist(),
            "input_errors_detected":handled,
            "explicit_drop_shape":list(validate_features(new.assign(note="memo"),extra="drop").shape),
            "new_predictions":model.predict(new).tolist()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
