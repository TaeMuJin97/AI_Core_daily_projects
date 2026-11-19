r"""
==============================================================================
[실습 보고서: Day 24 실습 05 - Chunk Span 범위 및 본문 일치 검증 (main.py)]
1. 실험 목적:
   - Embedding 및 DB 인덱싱 전에 각 Chunk의 문자 위치(char_start, char_end)가
     유효한 범위인지, 그리고 실제 clean_text 슬라이스와 본문이 100% 일치하는지 검증함.
2. 핵심 아키텍처 개념:
   - Span 경계 불변조건 검증 (D24-05-B01):
     char_start와 char_end가 정확한 정수(int)이며 0 <= start < end <= len(text)를
     만족하는지 먼저 확인하여 음수, 역전(start >= end), 범위 초과 오류를 차단함.
   - 원문 슬라이스 일치 및 빈 청크 방어 (D24-05-B02):
     길이가 같더라도 정제 버전이 꼬여 본문이 달라진 경우(span text mismatch)나
     공백만 남은 청크(empty content)를 ValueError로 즉시 실패시켜 오염된 벡터 저장을 막음.
==============================================================================
"""
"""실습 05 Basic · 유효한 위치인지 먼저 판단."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import save_json, show_success


def check_bounds(chunk: dict, text: str) -> None:
    # BEGIN D24-05-B01
    # [핵심 포인트 1: Span 범위(0 <= start < end <= len(text)) 및 정수 타입 검사]
    # - char_start, char_end가 int가 아니거나 유효 구간을 벗어나면 ValueError('invalid span')를 발생시킵니다.
    start, end = chunk["char_start"], chunk["char_end"]
    if type(start) is not int or type(end) is not int or not (0 <= start < end <= len(text)):
        raise ValueError("invalid span")
    # END D24-05-B01


def check_content(chunk: dict, text: str) -> None:
    # BEGIN D24-05-B02
    # [핵심 포인트 2: 본문 슬라이스 일치 여부 및 공백 전용 청크 차단]
    # - 먼저 check_bounds로 범위를 검증한 뒤, chunk['text']가 text[start:end]와 정확히 같은지 대조합니다.
    # - 공백만 있는 청크(not chunk['text'].strip())는 의미 없는 벡터를 만들므로 차단합니다.
    check_bounds(chunk, text)
    if chunk["text"] != text[chunk["char_start"] : chunk["char_end"]]:
        raise ValueError("span text mismatch")
    if not chunk["text"].strip():
        raise ValueError("empty content")
    # END D24-05-B02


def main():
    text = "10분 초과 시 결석으로 기록합니다."
    good = {"char_start": 0, "char_end": len(text), "text": text}
    bad = {"char_start": 0, "char_end": len(text), "text": "잘못된 내용"}
    check_content(good, text)
    try:
        check_content(bad, text)
    except ValueError:
        result = "expected failure"
    else:
        raise AssertionError("a corrupted chunk must fail")
    out = save_json(HERE, "span_check.json", {"good": "pass", "bad": result})
    show_success("05 Basic", out)


if __name__ == "__main__":
    main()