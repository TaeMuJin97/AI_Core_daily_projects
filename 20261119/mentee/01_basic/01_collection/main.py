"""
==============================================================================
[실습 보고서: Day 24 실습 01 - 원문 수집 및 바이트 무결성(SHA-256) 기록 (main.py)]
1. 실험 목적:
   - 문서 파싱·청킹(Chunking) 파이프라인의 첫 단계로, 원본 파일을 수정 없이 바이트(bytes)
     단위로 읽어들이고 고유 문서 ID와 SHA-256 해시를 메타데이터로 기록함.
2. 핵심 아키텍처 개념:
   - 원본 불변성 및 Fail-Fast (D24-01-B01):
     원문 파일을 텍스트로 섣불리 디코딩하지 않고 순수 bytes로 읽어 원본을 보존하며,
     파일이 존재하지 않을 경우 임의의 빈 값을 반환하지 않고 FileNotFoundError로 즉시 실패함.
   - 파일명과 문서 식별자 분리 (D24-01-B02):
     파일명(filename)은 언제든 바뀔 수 있으므로 식별자로 쓰지 않고, 별도의 doc_id와
     원본 바이트의 SHA-256 지문(raw_sha256)을 함께 묶어 변경 여부를 추적함.
==============================================================================
"""
"""실습 01 Basic · Python 파일 하나로 원문을 수집합니다."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import DATA, save_json, show_success
from coursekit.documents import sha_bytes


def read_raw(path: Path) -> bytes:
    """입력: Path / 출력: bytes. 원본 파일은 수정하지 않습니다."""
    # BEGIN D24-01-B01
    # [핵심 포인트 1: 원본 바이트 읽기]
    # - Path.read_bytes()는 파일을 바이너리 모드로 읽어 bytes를 반환합니다.
    # - 대상 경로에 파일이 없으면 자동으로 FileNotFoundError 예외를 발생시킵니다.
    return path.read_bytes()
    # END D24-01-B01


def build_record(doc_id: str, path: Path, raw: bytes) -> dict:
    """파일명은 식별자가 아닙니다. 문서 ID와 원본 바이트 해시를 별도로 보관합니다."""
    # BEGIN D24-01-B02
    # [핵심 포인트 2: 문서 메타데이터 및 SHA-256 해시 패키징]
    # - path.name으로 순수 파일명만 추출하고, raw의 길이(size_bytes)와
    #   sha_bytes(raw)로 생성한 64자리 SHA-256 해시를 딕셔너리로 묶습니다.
    return {
        "doc_id": doc_id,
        "filename": path.name,
        "size_bytes": len(raw),
        "raw_sha256": sha_bytes(raw),
    }
    # END D24-01-B02


def main():
    path = DATA / "raw" / "assignment.txt"
    raw = read_raw(path)
    record = build_record("DOC-ASSIGN", path, raw)
    assert record["size_bytes"] == len(raw)
    out = save_json(HERE, "collection.json", record)
    show_success("01 Basic", out)


if __name__ == "__main__":
    main()