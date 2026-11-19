"""
==============================================================================
[실습 보고서: Day 24 실습 02 - TXT 원문 UTF-8 디코딩 및 ParsedUnit 생성 (main.py)]
1. 실험 목적:
   - 수집된 원본 바이트(bytes)를 UTF-8로 명시적 디코딩하여 문자열(str)을 추출하고,
     출처 위치(source_locator)와 버전을 포함한 표준 ParsedUnit 레코드로 패키징함.
2. 핵심 아키텍처 개념:
   - 명시적 UTF-8 디코딩 및 누락 은닉 금지 (D24-02-B01):
     errors="ignore"를 사용하면 깨진 바이트가 조용히 삭제되어 원문 누락을 탐지할 수 없으므로,
     기본 strict 모드로 디코딩하여 잘못된 인코딩 입력 시 UnicodeDecodeError를 즉시 발생시킴.
   - 형식에 맞는 위치 메타데이터 기록 (D24-02-B02):
     TXT 문서에는 PDF와 같은 페이지 개념이 없으므로 가짜 page_number=1을 만들지 않고
     None으로 기록하며, unit_id와 source_locator로 원문 출처를 명시적으로 연결함.
==============================================================================
"""
"""실습 02 Basic · TXT parsing의 기본."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success


def decode_text(raw: bytes) -> str:
    """errors='ignore'를 쓰면 누락을 탐지하기 어렵습니다."""
    # BEGIN D24-02-B01
    # [핵심 포인트 1: 엄격한 UTF-8 디코딩]
    # - raw.decode("utf-8")은 기본값(errors="strict")으로 동작하여,
    #   잘못된 바이트 시퀀스가 섞여 있을 때 조용히 버리지 않고 UnicodeDecodeError를 발생시킵니다.
    return raw.decode("utf-8")
    # END D24-02-B01


def make_unit(doc_id: str, source_version: str, text: str) -> dict:
    """TXT에는 페이지 번호가 없으므로 None. 가짜 page 1을 만들지 않습니다."""
    # BEGIN D24-02-B02
    # [핵심 포인트 2: 표준 ParsedUnit 딕셔너리 생성]
    # - 추출된 원문(raw_text)을 문서 ID, 버전, 단위 ID, 출처 위치(source_locator)와 묶습니다.
    # - TXT에는 페이지가 없으므로 page_number는 반드시 None으로 유지합니다.
    return {
        "doc_id": doc_id,
        "source_version": source_version,
        "unit_id": "text-1",
        "source_locator": "assignment.txt",
        "page_number": None,
        "raw_text": text,
    }
    # END D24-02-B02


def main():
    raw = (DATA / "raw" / "assignment.txt").read_bytes()
    text = decode_text(raw)
    if not text.strip():
        raise ValueError("empty text")
    unit = make_unit("DOC-ASSIGN", "v1", text)
    out = save_json(HERE, "parsed_unit.json", unit)
    show_success("02 Basic", out)


if __name__ == "__main__":
    main()