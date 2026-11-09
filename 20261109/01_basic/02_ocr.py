"""
==============================================================================
[실습 보고서: 02_ocr.py - Tesseract 다중 페이지 일괄 OCR 호출 및 단어별 신뢰도(Confidence) 분석]
1. 실험 목적: 문서 이미지 3장(doc01~doc03.png)의 경로 목록을 텍스트 파일(p02_inputs.txt)로 묶어
              Tesseract 엔진을 단 1회 호출로 일괄 실행하고, 단어별 텍스트·위치·신뢰도(conf)를
              DataFrame 및 CSV(p02_words.csv)로 저장한 뒤 페이지별 평균 신뢰도를 산출함.
2. 핵심 개념 및 엔지니어링 포인트:
   - 다중 이미지 일괄 호출(Batch Input List): 이미지를 한 장씩 반복문으로 호출하면 매번 프로세스 생성 및
     모델 로딩 오버헤드가 발생함. 파일 경로 목록이 담긴 .txt 파일을 전달하면 엔진을 한 번만 띄워
     page_num(1, 2, 3...) 단위로 고속 처리할 수 있음.
   - 구조화된 출력(Output.DATAFRAME): 단순 문자열(image_to_string)이 아니라 단어별 좌표(left, top, width, height),
     계층 수준(level), 신뢰도(conf), 페이지 번호(page_num)를 표 형태로 한 번에 받아 후처리에 활용함.
   - 비단어 행(레이아웃 블록) 필터링: Tesseract TSV 출력에서 페이지·블록·문단·줄 헤더 행은 text가 비어 있고
     conf가 -1로 표시됨. 따라서 dropna(subset=['text'])와 conf >= 0 조건으로 실제 인식된 단어(level 5)만 정제함.
   - Confidence 해석 주의점: 출력된 신뢰도는 엔진 내부의 문자 매칭 점수일 뿐 실제 문맥상 정답 확률과 동일하지 않음.
3. 주요 산출물: p02_inputs.txt (입력 경로 목록), p02_words.csv (단어별 OCR 테이블)
==============================================================================
"""
"""실습 02: Tesseract를 실제 호출합니다. 엔진과 eng 언어팩이 필요합니다."""
from pathlib import Path
import os
import pandas as pd
import pytesseract

base = Path(__file__).resolve().parent

# [수정] Windows 환경에서 경로를 못 찾는 문제를 방지하기 위해 절대 경로를 직접 지정합니다.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

paths = [str(base / f'doc{i:02d}.png') for i in range(1, 4)]
input_list = base / 'p02_inputs.txt'
input_list.write_text('\n'.join(paths), encoding='utf-8')

# 여러 페이지를 목록으로 전달해 엔진을 한 번 호출합니다.
# TODO B02
# [핵심 구현: pytesseract.image_to_data를 이용한 다중 페이지 구조화 OCR 실행]
# - str(input_list): 이미지 3장의 경로가 적힌 p02_inputs.txt 파일 경로 전달 (1회 호출로 3페이지 연속 인식)
# - lang='eng': 영문 언어팩 지정
# - output_type=pytesseract.Output.DATAFRAME: 결과를 Pandas DataFrame으로 직접 반환받음
words = pytesseract.image_to_data(
    str(input_list),
    lang='eng',
    output_type=pytesseract.Output.DATAFRAME
)
# TODO 끝 B02

# [후처리 필터링: 레이아웃 구분 행(conf == -1 또는 빈 텍스트)을 제거하고 실제 단어 행만 남김]
words = words.dropna(subset=['text'])
words = words[words['conf'] >= 0]
words.to_csv(base / 'p02_words.csv', index=False, encoding='utf-8-sig')

for page, rows in words.groupby('page_num', sort=True):
    text = ' '.join(rows['text'].astype(str))
    print('page:', page, 'words:', len(rows), 'mean confidence:', round(rows['conf'].mean(), 2))
    print(text)
print('backend: live Tesseract; confidence는 정답 확률이 아닙니다.')