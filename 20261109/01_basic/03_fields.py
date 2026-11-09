"""
==============================================================================
[실습 보고서: 03_fields.py - 정규표현식을 이용한 문서 핵심 필드 추출 및 JSON 구조화]
1. 실험 목적: lesson.json에 기록된 OCR 원문(text)에서 정규표현식(Regex)을 활용하여
              발행일(issued_at), 공급자(supplier), 합계 금액(total_amount)을 추출하고,
              원문과 정규화된 값을 포함하는 구조화된 JSON(p03_fields.json)을 생성함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 정규표현식 활용(re.MULTILINE): 문서 내 여러 줄로 구성된 텍스트에서 각 줄의 시작(`^`)과 
     특정 키패턴(`DATE:`, `SUPPLIER:`, `TOTAL:`)을 정확히 매칭하기 위해 re.MULTILINE 플래그를 사용함.
   - 값의 정규화(Normalization)와 원본 보존(Traceability): 금액 문자열에 포함된 쉼표(`,`)를 제거하고 
     계산에 용이한 정수형(`int`)으로 변환하되, 추후 검증과 오류 추적을 위해 OCR 원문(`raw_text`)을 함께 저장함.
3. 주요 산출물: p03_fields.json (구조화된 문서 정보 및 메타데이터)
==============================================================================
"""
"""실습 03: 실제 OCR 기록에서 필요한 3개 필드를 추출합니다. 정상 자료만 사용합니다."""
from pathlib import Path
import json
import re

base = Path(__file__).resolve().parent
docs = json.loads((base / 'lesson.json').read_text(encoding='utf-8'))['documents']
records = []

for name in ['doc01', 'doc02', 'doc03']:
    text = docs[name]['ocr']['text']
    
    # DATE 줄 뒤의 날짜 부분을 추출합니다. OCR 원문도 함께 보존합니다.
    # TODO B03
    # [핵심 구현: 정규표현식으로 각 문서의 DATE 라인 매칭 및 발행일 값 추출]
    date_match = re.search(r'^DATE: (.+)$', text, re.MULTILINE)
    issued_at = date_match.group(1).strip() if date_match else ''
    # TODO 끝 B03
    
    supplier = re.search(r'^SUPPLIER: (.+)$', text, re.MULTILINE).group(1)
    
    # TODO B04
    # [핵심 구현: TOTAL 라인에서 쉼표가 포함된 금액 문자열을 추출한 뒤 int형으로 정규화]
    amount_match = re.search(r'^TOTAL: ([0-9,]+)', text, re.MULTILINE)
    if amount_match:
        total_amount = int(amount_match.group(1).replace(',', ''))
    else:
        total_amount = 0
    # TODO 끝 B04
    
    records.append({
        'document_id': name, 
        'issued_at': issued_at, 
        'supplier': supplier, 
        'total_amount': total_amount, 
        'currency': 'KRW', 
        'ocr_source': 'recorded Tesseract', 
        'raw_text': text
    })
    print(name, issued_at, supplier, total_amount)

(base / 'p03_fields.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')