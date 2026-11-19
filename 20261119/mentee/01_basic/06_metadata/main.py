r"""
==============================================================================
[실습 보고서: Day 24 실습 06 - Chunk Metadata 결합 및 Category 필터링 (main.py)]
1. 실험 목적:
   - 분할된 Chunk 본문에 원문 출처(doc_id, source_version, source_locator)와
     분류 정보(category)를 명시적으로 결합하고, 검색 대상 범위를 Metadata 조건으로
     사전 필터링하는 기본 계약을 구현함.
2. 핵심 아키텍처 개념:
   - 본문과 메타데이터의 분리 및 불변 복사 (D24-06-B01):
     기존 chunk 딕셔너리를 직접 변형하지 않고 {**chunk, ...} 언패킹으로 새 딕셔너리를 생성해
     출처 정보(doc_id, source_version, category, source_locator)를 안전하게 상속함.
   - 순서 보존 Metadata 필터링 (D24-06-B02):
     Top-k 거리 계산 전에 category 등 Metadata 조건으로 검색 대상 범위를 먼저 제한하며,
     리스트 컴프리헨션을 사용해 원본 청크의 순서를 그대로 유지함.
==============================================================================
"""
"""실습 06 Basic · 본문과 설명 정보를 나눕니다."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import save_json, show_success


def attach_metadata(chunk: dict, doc: dict) -> dict:
    # BEGIN D24-06-B01
    # [핵심 포인트 1: 원문 문서의 4대 핵심 메타데이터를 Chunk에 결합]
    # - doc_id, source_version, category, source_locator를 명시적으로 복사해
    #   검색 결과에서 원문 출처와 개정 버전을 역추적할 수 있게 합니다.
    return {
        **chunk,
        "doc_id": doc["doc_id"],
        "source_version": doc["source_version"],
        "category": doc["category"],
        "source_locator": doc["source_locator"],
    }
    # END D24-06-B01


def select_category(chunks: list[dict], category: str) -> list[dict]:
    # BEGIN D24-06-B02
    # [핵심 포인트 2: 주어진 category에 해당하는 Chunk만 순서 보존 필터링]
    # - 전체 후보에서 특정 분류(예: '학사')만 먼저 추려내어 검색 범위를 제한합니다.
    return [chunk for chunk in chunks if chunk["category"] == category]
    # END D24-06-B02


def main():
    a = attach_metadata(
        {"chunk_id": "C1", "body": "출석 안내"},
        {
            "doc_id": "DOC-ATTEND",
            "source_version": "v1",
            "category": "학사",
            "source_locator": "attendance.md#sec-1",
        },
    )
    b = attach_metadata(
        {"chunk_id": "C2", "body": "시설 안내"},
        {
            "doc_id": "DOC-FACILITY",
            "source_version": "v1",
            "category": "시설",
            "source_locator": "facility.html#main",
        },
    )
    selected = select_category([a, b], "학사")
    assert [r["chunk_id"] for r in selected] == ["C1"]
    out = save_json(HERE, "metadata.json", {"total": 2, "selected": selected})
    show_success("06 Basic", out)


if __name__ == "__main__":
    main()