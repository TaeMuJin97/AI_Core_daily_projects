"""Day5 실습 01 · 문제 정의와 입력 열 선택 · 심화."""
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

def inspect_stages(stages):
    """한 요청의 단계 로그가 여러 행인지 진단합니다.
    반환: rows, unique_requests, repeated_request_ids (정렬 목록).
    """
    # TODO D5-01-H1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-01-H1를 완성하세요.")

def mature_label_ids(labels, as_of):
    """UTC 관측 종료시각 <= as_of 이고 failed가 관측된(0/1) 요청 ID만 반환합니다.
    관측 기간이 미완료이거나 정답 미확인인 행을 성공(0)으로 채우지 않습니다.
    """
    # TODO D5-01-H2: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-01-H2를 완성하세요.")

def run():
    stages=pd.read_csv(DATA/"fixtures"/"stage_logs.csv")
    labels=pd.read_csv(DATA/"fixtures"/"label_windows.csv")
    return {"stage_audit":inspect_stages(stages),
            "matured_at_0915":mature_label_ids(labels,"2026-10-20T09:15:00Z")}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    args = parser.parse_args()
    emit(run(), args.output)
