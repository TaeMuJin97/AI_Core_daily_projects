r"""
==============================================================================
[실습 보고서: Day 24 실습 04 - 종료 조건이 있는 Character Window Chunking (main.py)]
1. 실험 목적:
   - 정제된 본문(clean_text)을 일정한 문자 길이(size)와 겹침(overlap)으로 분할하되,
     잘못된 파라미터 입력과 본문 끝에서의 불필요한 꼬리 청크 생성을 방지함.
2. 핵심 아키텍처 개념:
   - 파라미터 계약 검증 (D24-04-B01):
     size와 overlap이 정확한 정수(int)인지 검사하고 0 <= overlap < size를 강제함.
     만약 overlap >= size이면 start가 전진하지 못해 무한 루프에 빠지므로 사전 차단함.
   - 슬라이싱 범위 [start, end) 및 종료 조건 (D24-04-B02):
     Python 슬라이싱 규칙에 따라 char_end는 제외 끝점으로 기록하며,
     마지막 청크가 원문 끝(end == len(text))에 닿으면 즉시 break로 종료하여
     이미 포함된 꼬리 구간만 중복 생성되는 오류를 방지함.
==============================================================================
"""
"""실습 04 Basic · 종료 조건이 중요한 문자 창."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success


def check_params(size: int, overlap: int) -> None:
    # BEGIN D24-04-B01
    # [핵심 포인트 1: 정수 타입 및 0 <= overlap < size 범위 검증]
    # - overlap이 음수이거나 size 이상이면 슬라이딩 윈도우가 전진하지 못하므로 ValueError를 발생시킵니다.
    if type(size) is not int or type(overlap) is not int or not (0 <= overlap < size):
        raise ValueError("invalid chunk size or overlap")
    # END D24-04-B01


def make_windows(text: str, size: int, overlap: int) -> list[dict]:
    """본문 끝에서 반복문을 종료하지 않으면 겹친 꼬리 청크가 생깁니다."""
    # BEGIN D24-04-B02
    # [핵심 포인트 2: [start, end) 구간 분할 및 원문 끝 도달 시 즉시 종료]
    # - end == len(text)에서 break 하지 않으면 start = end - overlap으로 되돌아가
    #   이미 마지막 청크에 포함된 꼬리 부분만 잘린 중복 청크가 하나 더 생깁니다.
    check_params(size, overlap)
    spans = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        spans.append({"char_start": start, "char_end": end, "text": text[start:end]})
        if end == len(text):
            break
        start = end - overlap
    return spans
    # END D24-04-B02


def main():
    text = "가" * 71
    chunks = make_windows(text, size=40, overlap=10)
    assert [(c["char_start"], c["char_end"]) for c in chunks] == [
        (0, 40),
        (30, 70),
        (60, 71),
    ]
    out = save_json(
        HERE, "chunks.json", {"source": "71-character teaching fixture", "chunks": chunks}
    )
    show_success("04 Basic", out)


if __name__ == "__main__":
    main()