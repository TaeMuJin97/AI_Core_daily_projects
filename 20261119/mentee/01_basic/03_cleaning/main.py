r"""
==============================================================================
[실습 보고서: Day 24 실습 03 - 일반 본문(Prose) 전용 Text Cleaning (main.py)]
1. 실험 목적:
   - 파싱된 원문에서 검색을 방해하는 형식상의 잡음(운영체제별 줄바꿈 차이, 연속 가로 공백)만
     최소한으로 정리하고, 숫자·조건·예외·문단 경계 등 원문의 의미는 그대로 보존함.
2. 핵심 아키텍처 개념:
   - 줄바꿈 통일 및 순서 중요성 (D24-03-B01):
     Windows의 CRLF(\r\n)와 구형 CR(\r)을 LF(\n)로 통일하되, 반드시 \r\n을 먼저 치환해야
     빈 줄이 의도치 않게 두 배로 늘어나는 오류를 방지할 수 있음.
   - 줄 단위 가로 공백 축소 및 문단 보존 (D24-03-B02):
     전체 텍스트에서 \s+를 치환하면 문단 구분용 줄바꿈(\n\n)까지 날아가므로,
     text.split('\n')으로 줄을 나눈 뒤 각 줄의 가로 공백([ \t]+)만 한 칸으로 축소함.
     (단, 들여쓰기가 중요한 코드 블록이나 정렬된 표·TSV에는 이 규칙을 그대로 쓰지 않음)
==============================================================================
"""

"""실습 03 Basic · 일반 prose 전용 cleaning."""
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success


def unify_newlines(text: str) -> str:
    # BEGIN D24-03-B01
    # [핵심 포인트 1: CRLF(\r\n) → CR(\r) 순서로 LF(\n) 통일]
    # - \r\n을 먼저 \n으로 바꾼 뒤 남은 단독 \r을 \n으로 바꾸어 문단 줄바꿈을 보존합니다.
    return text.replace("\r\n", "\n").replace("\r", "\n")
    # END D24-03-B01


def reduce_horizontal_spaces(text: str) -> str:
    """줄 단위 변환이므로 빈 줄이 사라지지 않습니다."""
    # BEGIN D24-03-B02
    # [핵심 포인트 2: 줄 단위 가로 공백·탭 축소 및 빈 줄 유지]
    # - text.split('\n')으로 줄 단위로 순회하며 가로 공백([ \t]+)만 한 칸으로 줄입니다.
    # - 빈 줄은 ''로 남아 '\n'.join(...) 시 문단 경계('\n\n')가 그대로 유지됩니다.
    return "\n".join(
        re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")
    ).strip()
    # END D24-03-B02


def main():
    text = "출석   안내\r\n\r\n10분  초과는 결석.\r\n단,  사전 승인 시 예외."
    cleaned = reduce_horizontal_spaces(unify_newlines(text))
    assert "10분 초과는 결석." in cleaned
    assert "\n\n" in cleaned
    out = save_json(HERE, "cleaning.json", {"before": repr(text), "after": cleaned})
    show_success("03 Basic", out)


if __name__ == "__main__":
    main()