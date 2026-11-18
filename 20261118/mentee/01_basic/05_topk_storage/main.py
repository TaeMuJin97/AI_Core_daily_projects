"""
==============================================================================
[실습 보고서: Day 23 실습 05 - pgvector 원문·벡터 통합 저장 및 Exact Top-k 검색 (main.py)]
1. 실험 목적:
   - 지식 원문(101~109)과 384차원 E5 임베딩 벡터를 PostgreSQL의 한 행(Row)으로 결합하여 저장하고,
     질의 벡터와의 Cosine Distance(<=>) 오름차순(ASC) 정렬을 통해 가장 가까운 Top-k 후보를 조회함.
2. 핵심 아키텍처 개념:
   - 검색 전용 테이블 분리 설계 (D23-05-B01):
     기존 CRUD용 knowledge 테이블을 삭제(DROP)하거나 변형하지 않고, 별도의 'day23_search_docs'
     테이블을 생성하여 운영 데이터 보존과 벡터 인덱스 실험을 분리함.
   - 원문-벡터 행 순서(Row Alignment) 보장 (D23-05-B02):
     지식 목록의 순서와 임베딩 행렬(n, 384)의 행 인덱스가 조금이라도 어긋나면 ID=102에 101번의
     벡터가 들어가는 치명적 정합성 오류가 발생하므로, 입력 순서를 엄격히 유지하고 Upsert로 원자적 갱신을 수행함.
   - 모델 공간 오염 방지 및 Exact Top-k SQL (D23-05-B03):
     동일한 384차원이라도 다른 모델이 만든 벡터와 비교하면 수학적 의미가 깨지므로 WHERE embedding_model = %s
     조건을 걸고, 거리 연산자(<=>) 기준 오름차순(ASC)으로 정렬하여 가장 가까운 k건을 반환함.
==============================================================================
"""
"""Day23 실습 05 · 원문·벡터 저장과 Top-k (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from day23kit.data import load_knowledge, passage_text, E5_MODEL_ID, TABLE_NAME
from day23kit.fixtures import fixture_search
from day23kit.embedding import (
    get_encoder,
    encode_passages,
    encode_question,
    validate_vectors,
)
from day23kit.db import (
    connect_db,
    ensure_table,
    upsert_rows,
    exact_topk,
    TABLE_SQL,
    SQL_TOPK,
)
from day23kit.io import save_result


# BEGIN D23-05-B01
def schema_sql():
    """
    TODO D23-05-B01 · schema_sql
        기존 knowledge 테이블을 건드리지 않는 day23_search_docs의 CREATE TABLE SQL을 작성하세요.
        필드: id(PK),title,content,category,source_version,embedding_model,embedding vector(384).
        DROP/TRUNCATE를 사용하지 않습니다.
    """
    # [핵심 포인트 1: 원문 메타데이터와 384차원 벡터를 한 행에 묶는 비파괴적(IF NOT EXISTS) DDL 설계]
    # - DROP이나 TRUNCATE를 쓰지 않아 기존 데이터를 안전하게 보호합니다.
    # - vector(384) 타입은 DB 차원에서 384차원이 아닌 배열의 INSERT를 원천 차단합니다.
    # - embedding_model 컬럼을 함께 두어 어떤 모델 가중치로 생성된 벡터인지 추적합니다.
    return """
CREATE TABLE IF NOT EXISTS day23_search_docs (
    id integer PRIMARY KEY,
    title text NOT NULL,
    content text NOT NULL,
    category text NOT NULL,
    source_version text NOT NULL,
    embedding_model text NOT NULL,
    embedding vector(384) NOT NULL
);
""".strip()
# END D23-05-B01


# BEGIN D23-05-B02
def prepare_document_rows(rows):
    """
    TODO D23-05-B02 · prepare_document_rows
        지식 101~109의 ID/제목/본문/분류/버전 및 passage 입력을 순서대로 묶으세요.
        반환: [{'id', 'passage_input', ...}, ...]. 같은 ID를 새로 만들지 않습니다.
    """
    # [핵심 포인트 2: 지식 101~109의 ID 불변 유지 및 E5 passage 입력 순서 고정]
    # - 새 ID를 임의로 채번하지 않고 원본 지식의 ID(101~109)와 순서를 그대로 유지합니다.
    # - 각 행마다 passage_text(r)로 'passage: {title} {content}' 문자열을 조립해 매핑합니다.
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "content": r["content"],
            "category": r["category"],
            "source_version": r["source_version"],
            "passage_input": passage_text(r),
        }
        for r in rows
    ]
# END D23-05-B02


# BEGIN D23-05-B03
def topk_sql():
    """
    TODO D23-05-B03 · topk_sql
        Cosine distance(<=>) 오름차순, k개 제한 SQL을 작성하세요.
        SELECT에 id,title,content,category,source_version,embedding_model,distance 포함.
        E5 외 다른 공간 혼합을 막도록 embedding_model을 필터합니다.
    """
    # [핵심 포인트 3: 모델 공간 필터(embedding_model) 및 Cosine Distance(<=>) 오름차순(ASC) Top-k 쿼리]
    # - <=> 연산자는 유사도가 아니라 '거리(1 - Cosine Similarity)'이므로 값이 작을수록(ASC) 가까운 문서입니다.
    # - 서로 다른 임베딩 모델의 벡터가 섞여 잘못된 거리가 계산되는 것을 막기 위해 WHERE embedding_model = %s를 지정합니다.
    # - 파라미터 바인딩 순서: (질의벡터 qvec, 모델ID embedding_model, 질의벡터 qvec, 제한개수 k)
    return """
SELECT id, title, content, category, source_version, embedding_model,
       embedding <=> %s AS distance
FROM day23_search_docs
WHERE embedding_model = %s
ORDER BY embedding <=> %s ASC
LIMIT %s;
""".strip()
# END D23-05-B03


def run(mode, level, args):
    rows = load_knowledge()
    sql_schema = schema_sql()
    inputs = prepare_document_rows(rows)
    sql_query = topk_sql()
    question = "서버는 어디에서 실행하나요?"
    result = dict(
        exercise=5,
        level=level,
        source_mode="simulated" if mode == "fixture" else "pgvector_exact",
        table=TABLE_NAME,
        model=E5_MODEL_ID,
        prepared_count=len(inputs),
        first_passage=inputs[0]["passage_input"],
        sql_schema=sql_schema,
        sql_topk=sql_query,
    )
    category = None if level == 1 else "development"
    if level >= 2:
        result["sql_filtered"] = filtered_sql()
        result["options"] = check_search_options(3, category)
    if mode == "fixture":
        hits = fixture_search(question, 3, category=category)
    else:
        encoder = get_encoder("live")
        vectors = encode_passages(encoder, rows)
        if level >= 3:
            check_id_vector_integrity(rows, vectors)
        else:
            validate_vectors(vectors, len(rows))
        qvec = encode_question(encoder, question)
        with connect_db(Path(__file__).with_name(".env")) as conn:
            ensure_table(conn)
            upsert_rows(conn, rows, vectors, E5_MODEL_ID)
            hits = exact_topk(conn, qvec, k=3, category=category)
    result["hits"] = [
        {
            "id": h["id"],
            "content": h["content"],
            "distance": round(h["distance"], 6),
        }
        for h in hits
    ]
    if level >= 3:
        # 이전 단계의 벡터를 재사용합니다. live에서는 같은 모델을 다시 다운로드/로드하지 않습니다.
        if mode == "fixture":
            encoder = get_encoder("fixture")
            vectors = encode_passages(encoder, rows)
        result["id_vector_integrity"] = check_id_vector_integrity(rows, vectors)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 05 · 원문·벡터 저장과 Top-k"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_05.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()