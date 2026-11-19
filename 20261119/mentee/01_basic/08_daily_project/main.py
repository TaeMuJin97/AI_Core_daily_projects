r"""
==============================================================================
[실습 보고서: Day 24 실습 08 - End-to-End Ingestion 파이프라인 연결 및 검증 리포트 (main.py)]
1. 실험 목적:
   - Day 24에서 단계별로 구현한 Collect → Parse → Clean → Chunk → Validate 과정을
     하나의 파이프라인으로 연결하고, 전처리 완료 상태와 검증 결과를 리포트로 기록함.
   - 오늘의 범위는 검색 가능한 Chunk 준비까지이며, LLM 답변 생성은 다음 차시(Basic RAG)에서 연결함.
2. 핵심 아키텍처 개념:
   - 단계별 입출력 계약 연결 (D24-08-B01):
     parse_one()의 결과 중 status == 'parsed'인 문서만 통과시키고,
     ParsedUnit['raw_text'] → clean_prose() → char_windows(110, 15) → build_chunk() 순으로 연결함.
   - 최종 Chunk 검증 및 상태 정직성 (D24-08-B02):
     최종 Chunk의 본문(c['body'])을 중간 Span의 'text'로 명시적 매핑해 validate_span()으로 검증하며,
     실제 DB 적재나 임베딩을 수행하지 않았으므로 status를 'published'가 아닌 'prepared'로 기록함.
==============================================================================
"""
"""실습 08 Basic · Checkpoint를 연결합니다. LLM 답변 생성은 하지 않습니다."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import save_json, show_success
from coursekit.documents import by_doc, parse_one
from coursekit.processing import clean_prose, char_windows, build_chunk, validate_span


def run_pipeline(doc_id: str) -> tuple[dict, str, list[dict]]:
    # BEGIN D24-08-B01
    # [핵심 포인트 1: Parse → Clean → Chunk 단일 파이프라인 연결]
    # - 파싱 상태가 'parsed'가 아니면 즉시 ValueError로 중단(Fail-Fast)합니다.
    # - unit['raw_text']를 정제한 뒤 110자/15자 overlap 설정으로 청크 목록을 생성합니다.
    doc = by_doc(doc_id)
    result = parse_one(doc)
    if result["status"] != "parsed":
        raise ValueError("parse not ready")
    unit = result["units"][0]
    clean = clean_prose(unit["raw_text"])
    chunks = [build_chunk(doc, unit, clean, span) for span in char_windows(clean, 110, 15)]
    return doc, clean, chunks
    # END D24-08-B01


def check_report(doc: dict, clean: str, chunks: list[dict]) -> dict:
    # BEGIN D24-08-B02
    # [핵심 포인트 2: 청크 전수 검증(doc_id·Span 일치) 및 준비 완료 리포트 생성]
    # - 최종 Chunk에는 'text' 키가 없으므로 c['body']를 validate_span의 'text'로 연결해 검증합니다.
    # - 실제 Embedding·DB 적재 전 단계이므로 status는 'prepared'로 기록합니다.
    if not chunks:
        raise ValueError("empty chunk list")
    for c in chunks:
        if c["doc_id"] != doc["doc_id"]:
            raise ValueError("doc_id mismatch")
        validate_span(
            {"char_start": c["char_start"], "char_end": c["char_end"], "text": c["body"]},
            clean,
        )
    return {
        "doc_id": doc["doc_id"],
        "status": "prepared_not_embedded",
        "chunk_count": len(chunks),
        "source_versions": [doc["source_version"]],
        "chunk_ids": [c["chunk_id"] for c in chunks],
    }
    # END D24-08-B02


def main():
    doc, clean, chunks = run_pipeline("DOC-ASSIGN")
    report = check_report(doc, clean, chunks)
    out = save_json(HERE, "daily_project.json", {"report": report, "chunks": chunks})
    show_success("08 Basic", out)


if __name__ == "__main__":
    main()