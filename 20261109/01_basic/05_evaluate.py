"""
==============================================================================
[실습 보고서: 05_evaluate.py - 5문서×3필드 OCR 추출 정확도(Exact Match) 평가]
1. 실험 목적: 5개 문서(doc01~doc05)의 OCR 텍스트에서 추출한 3개 핵심 필드(발행일, 공급자, 합계)를
              실제 정답(truth)과 비교해 일치율을 계산하고 CSV 리포트(p05_field_scores.csv)로 저장함.
2. 핵심 포인트:
   - 업무 필드 단위 평가: OCR 원문에 일부 오타(예: DOCO1)가 있더라도, 실제 우리가 필요한 
     핵심 3개 필드가 정확히 추출되었는지(Field-level Accuracy)를 중점적으로 평가함.
   - 정답 분리(Data Leakage 방지): 추출 단계에서는 OCR 텍스트만 보고, 정답(truth)은 채점(TODO B06)할 때만 확인함.
   - 타입 통일: 정답 금액이 정수(int)이므로 추출한 문자열 금액도 int()로 변환해 비교함.
3. 주요 산출물: p05_field_scores.csv (총 15개 필드의 채점 결과표 - 포트폴리오용 Git 업로드 대상)
==============================================================================
"""
"""실습 05: 5문서×3필드의 일치율을 구합니다. 정답은 평가할 때만 읽습니다."""
from pathlib import Path
import json
import re
import pandas as pd

# 기본 경로 설정 및 lesson.json 로드 (이전 실습과 동일)
base = Path(__file__).resolve().parent
lesson = json.loads((base / 'lesson.json').read_text(encoding='utf-8'))
rows = []

for name, doc in lesson['documents'].items():
    text = doc['ocr']['text']  # 추출 단계에서는 정답(truth)이 아닌 OCR 텍스트만 사용
    
    # [중요] 정규표현식으로 3개 핵심 필드 추출 및 데이터 타입 정규화
    # - issued_at   : 'DATE: ' 뒤의 YYYY-MM-DD(\d{4}-\d{2}-\d{2}) 날짜 패턴 추출
    # - supplier    : 'SUPPLIER: ' 뒤의 해당 줄 텍스트(.+) 추출
    # - total_amount: 'TOTAL: ' 뒤의 연속된 숫자(\d+)를 찾아 정답과의 비교를 위해 정수(int)로 변환
    predicted = {
        'issued_at': re.search(r'DATE: (\d{4}-\d{2}-\d{2})', text).group(1),
        'supplier': re.search(r'SUPPLIER: (.+)', text).group(1),
        'total_amount': int(re.search(r'TOTAL: (\d+)', text).group(1))
    }
    
    for field in ['issued_at', 'supplier', 'total_amount']:
# TODO B06
        # [핵심 구현: OCR 예측값과 실제 정답(Ground Truth)의 일치 여부 판정]
        # - predicted[field]   : OCR 텍스트에서 정규표현식으로 뽑아낸 예측값
        # - doc['truth'][field]: lesson.json에 기록된 실제 정답 (채점 시점에만 꺼내서 비교)
        # - 값과 자료형(str/int)이 모두 같으면 True, 다르면 False가 저장됨
        correct = (predicted[field] == doc['truth'][field])
# TODO 끝 B06
        rows.append({
            'document_id': name,
            'field': field,
            'predicted': predicted[field],
            'correct': correct
        })

# 채점 결과를 표(DataFrame)로 변환 후 엑셀에서 한글/기호가 깨지지 않도록 utf-8-sig로 저장
table = pd.DataFrame(rows)
table.to_csv(base / 'p05_field_scores.csv', index=False, encoding='utf-8-sig')

# 전체 문서/필드 수 및 True(1)의 합계를 통한 최종 일치 건수(15 / 15) 출력
print('문서 수:', len(lesson['documents']), '필드 수:', len(table))
print('필드 일치:', int(table['correct'].sum()), '/', len(table))
print('합성 영어 문서의 기록 비교이며 일반 OCR·한국어 성능이 아닙니다.')