"""
==============================================================================
[실습 보고서: 05_metrics.py - 학습 로그(metrics_example.csv)에서 최고 성능 Epoch 탐색]
1. 실험 목적: 검증 결과가 기록된 CSV 파일로부터 mAP50-95 지표를 기준으로 
              가장 성능이 우수한 최적의 Epoch 행을 자동으로 찾아냄.
2. 핵심 개념 및 엔지니어링 포인트:
   - idxmax() 활용: Pandas Series에서 값이 가장 큰 원소의 인덱스(Row Index)를 찾아 반환함.
   - loc 기반 행 추출: idxmax()로 얻은 인덱스를 .loc[]에 전달해 해당 행 전체 데이터를 추출함.
   - mAP의 의미: mAP는 단순 분류 Accuracy가 아니라, 검증(valid) 세트에서 
     박스의 위치 정확도와 클래스 분류를 동시에 평가한 누적 지표임.
3. 주요 산출물: 터미널에 최적 에폭 번호 및 mAP50, mAP50-95 지표 출력
==============================================================================
"""
"""실습 05. 가상 기록 읽기. 이 표는 실제 모델 성능이 아닙니다."""
from pathlib import Path
import pandas as pd

# BASE = Path(__file__).resolve().parent
BASE = Path(".")  # 한글 폴더명 경로 우회용 상대 경로 설정

# 검증 지표가 기록된 CSV 로그 파일을 Pandas DataFrame으로 읽어옵니다.
history = pd.read_csv(BASE / "data/metrics_example.csv")

# >>> B06
# 요구: map50_95가 가장 큰 행을 선택하세요. idxmax는 첫 최대값의 index를 반환합니다.
# [핵심 구현: idxmax와 .loc을 이용한 최고 성능 행 추출]
# 1) history["map50_95"]: map50_95 열(Column)만 추출하여 Series로 만듦
# 2) .idxmax(): 해당 열에서 값이 가장 큰 행의 인덱스를 찾아냄
# 3) history.loc[...]으로 해당 인덱스의 모든 컬럼 데이터(에폭, loss, map50 등)를 묶어서 best에 대입
best = history.loc[history["map50_95"].idxmax()]
# <<< B06

print("자료 종류: 읽기 연습용 가상 기록 — 실제 YOLO 성능 아님")
print("선택 epoch:", int(best["epoch"]))
print("mAP50:", best["map50"], "mAP50-95:", best["map50_95"])
print("mAP는 accuracy가 아닙니다. train이 아니라 valid의 위치·분류 평가 기록입니다.")