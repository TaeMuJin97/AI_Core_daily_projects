r"""
==============================================================================
[실습 보고서: Day 24 실습 07 - pgvector Indexing 데이터 계약 및 Live DB 저장·조회 (main.py)]
1. 실험 목적:
   - 검증된 Chunk가 E5 본문 입력 계약('passage: ')을 만족하는지 확인하고,
     PostgreSQL pgvector의 Staging → Publish → Search 결과 행을 표준 딕셔너리로 변환함.
   - 기본 실행(prepared_only_not_db)과 실제 E5·DB 연동(--live-db) 경로를 명확히 분리함.
2. 핵심 아키텍처 개념:
   - 인덱싱 전 E5 입력 계약 확인 (D24-07-B01):
     파싱 상태가 'parsed'인 문서에서만 청크를 추출하고, 빈 본문이나 'passage: ' 접두어가
     누락된 청크는 임베딩 전에 ValueError로 차단함.
   - 정수 citation_id 기반 검색 결과 직렬화 (D24-07-B02):
     11/16 KnowledgeAnswer.source_ids(list[int]) 계약과 호환되도록 양의 정수 citation_id를
     검증하고, chunk_id·body·source_locator·doc_id·source_version·cosine_distance를 반환함.
   - 트랜잭션 외부 추론 원칙 (--live-db):
     무거운 E5 모델 인코딩(encode_passages, encode_query)은 DB 트랜잭션 진입 전에 완료하고,
     with conn.transaction() 내부에서는 stage_version과 publish_version만 짧게 원자적으로 수행함.
==============================================================================
"""
"""실습 07 Basic · 기본 실행은 데이터 계약, --live-db는 실제 E5/DB 실행."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from coursekit.io import save_json, show_success
from coursekit.documents import by_doc, parse_one
from coursekit.processing import make_chunks


def select_index_chunk(doc_id: str) -> tuple[dict, dict]:
    # BEGIN D24-07-B01
    # [핵심 포인트 1: 파싱 성공 문서에서 첫 번째 유효 Chunk 선택 및 E5 접두어 검증]
    # - chunks[0]의 본문이 비어 있지 않고, embedding_text가 'passage: '로 시작하는지 확인합니다.
    doc = by_doc(doc_id)
    parsed = parse_one(doc)
    if parsed["status"] != "parsed":
        raise ValueError("not indexable")
    chunks = make_chunks(doc, parsed["units"][0], size=110, overlap=15)
    first = chunks[0]
    if not first["body"].strip() or not first["embedding_text"].startswith("passage: "):
        raise ValueError("bad embedding input")
    return doc, first
    # END D24-07-B01


def format_hit(row: tuple) -> dict:
    """DB 행: citation_id,chunk_id,body,locator,doc_id,version,distance."""
    # BEGIN D24-07-B02
    # [핵심 포인트 2: DB 검색 결과 튜플을 표준 출처·거리 딕셔너리로 변환]
    # - citation_id는 양의 정수(int, > 0)여야 하며, cosine_distance는 float로 변환해 반환합니다.
    cid, chunk_id, body, locator, doc_id, source_version, distance = row
    if type(cid) is not int or cid <= 0:
        raise ValueError("invalid citation ID")
    return {
        "citation_id": cid,
        "chunk_id": chunk_id,
        "body": body,
        "source_locator": locator,
        "doc_id": doc_id,
        "source_version": source_version,
        "cosine_distance": float(distance),
    }
    # END D24-07-B02


def main():
    doc, chunk = select_index_chunk("DOC-ASSIGN")
    output = {
        "source_mode": "prepared_only_not_db",
        "chunk": chunk,
        "live_db": "not_run",
        "sample_hit_contract": format_hit(
            (
                201,
                chunk["chunk_id"],
                chunk["body"],
                chunk["source_locator"],
                doc["doc_id"],
                "v1",
                0.0,
            )
        ),
    }
    if "--live-db" in sys.argv:
        from coursekit.live import (
            connect_db,
            load_encoder,
            encode_passages,
            encode_query,
        )
        from coursekit.db import (
            initialize,
            stage_version,
            publish_version,
            search_current,
            use_schema,
        )

        # 실제 모델 추론은 DB 트랜잭션 전에 수행합니다.
        model = load_encoder()
        vectors = encode_passages(model, [chunk])
        query = encode_query(model, "과제 파일은 어디에 보관하나요?")
        with connect_db() as conn:
            use_schema(conn, "d24_basic07")
            initialize(conn)
            with conn.transaction():
                stage_version(conn, doc, doc["file"], [chunk], vectors)
                publish_version(
                    conn,
                    doc["doc_id"],
                    doc["source_version"],
                    chunk["pipeline_version"],
                )
            result = search_current(conn, query, category="학사", k=3)
            output["source_mode"] = "e5_pgvector_live"
            output["live_db"] = [format_hit(r) for r in result]
    out = save_json(HERE, "indexing.json", output)
    show_success("07 Basic", out)


if __name__ == "__main__":
    main()