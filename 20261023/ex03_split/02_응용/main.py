"""Day5 실습 03 · 60·20·20 분할과 무결성 검사 · 응용."""
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

def split_fixed(X,y,seed=42):
    """제공: 실습 03 기본필수에서 배운 두 단계 분할을 재사용합니다."""
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.20,random_state=seed,stratify=y)
    X_train,X_valid,y_train,y_valid=train_test_split(X_dev,y_dev,test_size=.25,random_state=seed,stratify=y_dev)
    return {"train":(X_train,y_train),"valid":(X_valid,y_valid),"test":(X_test,y_test)}

def summarize_splits(parts,seed):
    """seed, sizes, class_counts와 각 부분의 ID 순서(ids)를 JSON 저장 가능한 dict로 반환."""
    # TODO D5-03-A1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-A1를 완성하세요.")

def changed_training_ids(original, reordered):
    """두 분할에서 train 소속이 달라진 ID 개수를 반환합니다(대칭차집합).
    행 순서만 바꾼 별도 시연이며 기본 원본/분할표를 덮어쓰지 않습니다.
    """
    # TODO D5-03-A2: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-03-A2를 완성하세요.")

def run():
    X,y=load_xy()
    parts=split_fixed(X,y)
    reversed_parts=split_fixed(X.iloc[::-1],y.iloc[::-1])
    summary=summarize_splits(parts,42)
    # 화면에는 ID 전체 대신 변경 건수만 출력; 전체 기록은 결과 JSON의 ids에 남습니다.
    summary["changed_train_ids_after_reorder"]=changed_training_ids(parts,reversed_parts)
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
