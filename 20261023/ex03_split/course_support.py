"""제공 코드: 경로·CSV 읽기·JSON 출력. 전처리기를 학습하지 않습니다."""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
NUM = ["input_chars", "allowed_tools"]
CAT = ["task_type", "priority"]
FEATURES = NUM + CAT
FORBIDDEN = {"failed", "status", "elapsed_ms", "retry_count", "request_id"}

def read_table(path):
    """파일의 빈칸만 NaN으로 읽습니다. 학습 통계로 채우지 않습니다."""
    frame = pd.read_csv(Path(path), encoding="utf-8", dtype={"request_id": str})
    for col in CAT:
        if col in frame:
            s = frame[col].astype(object)
            frame[col] = s.where(pd.notna(s), np.nan)
    return frame

def load_raw():
    return read_table(DATA / "requests.csv")

def load_xy():
    """제공: 02교시 이후 이전 단원 입력 선택을 재사용합니다."""
    frame = load_raw().set_index("request_id")
    return frame[FEATURES].copy(), frame["failed"].copy()

def load_dev():
    """제공: 04~06교시 고정 train·valid 체크포인트. test 파일을 읽지 않습니다."""
    tr = read_table(DATA / "checkpoints" / "train.csv").set_index("request_id")
    va = read_table(DATA / "checkpoints" / "valid.csv").set_index("request_id")
    return tr[FEATURES].copy(), va[FEATURES].copy(), tr["failed"].copy(), va["failed"].copy()

def new_requests():
    return read_table(DATA / "new_requests.csv").set_index("request_id")

def json_ready(value):
    """JSON에 NaN·Infinity를 쓰지 않고 null로 표현하는 출력 보조 함수."""
    if isinstance(value, dict):
        return {str(k):json_ready(v) for k,v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray, pd.Index)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value

def emit(result, output):
    """학생이 계산한 결과를 보여 주고 저장합니다. expected_outputs를 읽지 않습니다."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    text=json.dumps(json_ready(result), ensure_ascii=False, indent=2, allow_nan=False)
    (output / "result.json").write_text(text+"\n", encoding="utf-8")
    print(text)
