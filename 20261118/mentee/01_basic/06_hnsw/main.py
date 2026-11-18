"""
==============================================================================
[실습 보고서: Day 23 실습 06 - Exact Search vs HNSW ANN 인덱스 및 EXPLAIN 실행 계획 분석 (main.py)]
1. 실험 목적:
   - pgvector의 근사 최근접 이웃(ANN: Approximate Nearest Neighbor) 인덱스인 HNSW 생성 문법을 익히고,
     PostgreSQL의 EXPLAIN (ANALYZE, BUFFERS) 실행 계획을 통해 실제 스캔 방식(Seq Scan vs Index Scan)을
     추측이 아닌 실측 데이터로 판독함.
2. 핵심 아키텍처 개념:
   - HNSW 인덱스와 연산자 클래스(Operator Class) 일치 계약 (D23-06-B01):
     검색 쿼리에서 Cosine Distance 연산자(<=>)를 사용하려면 인덱스 생성 시 반드시 'vector_cosine_ops'를
     지정해야 함. (L2 거리 <->는 vector_l2_ops, 내적 <#>는 vector_ip_ops와 짝을 이룸)
   - EXPLAIN (ANALYZE, BUFFERS)를 통한 실행 계획 검증 (D23-06-B02):
     인덱스 DDL을 실행했다고 해서 무조건 인덱스가 타는 것이 아니므로, 반드시 EXPLAIN으로 쿼리 플래너의
     실제 선택을 확인해야 함. 바인딩 파라미터(%s 2개)는 (E5_MODEL_ID, qvec) 순서와 일치시킴.
   - 소규모 테이블(9건)에서의 Seq Scan 선택 원리 (D23-06-B03):
     데이터가 9건뿐일 때는 HNSW 그래프 메타데이터 페이지를 타고 이동하는 랜덤 I/O 비용보다,
     테이블 페이지 1개를 통째로 읽는 순차 스캔(Seq Scan)이 훨씬 저렴하므로 PostgreSQL 옵티마이저가
     Seq Scan을 선택하는 것이 완전히 정상적인 동작임.
==============================================================================
"""
"""Day23 실습 06 · Exact·HNSW·EXPLAIN (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from day23kit.data import E5_MODEL_ID
from day23kit.embedding import get_encoder, encode_question
from day23kit.db import connect_db, exact_topk, check_data_ready, HNSW_SQL
from day23kit.io import save_result


# BEGIN D23-06-B01
def create_index_sql():
    """
    TODO D23-06-B01 · create_index_sql
        day23_search_docs.embedding의 Cosine HNSW 인덱스를 정의하세요.
        USING hnsw (embedding vector_cosine_ops)를 사용합니다.
        인덱스는 선택 항목이며 9건에서 빠른 성능을 보장하지 않습니다.
    """
    # [핵심 포인트 1: Cosine Distance(<=>) 전용 HNSW 인덱스 DDL 정의]
    # - USING hnsw (embedding vector_cosine_ops)를 지정하여 <=> 연산자 정렬 시 활용될 수 있도록 구성합니다.
    # - IF NOT EXISTS를 사용하여 반복 실행 시에도 에러 없이 멱등성(Idempotency)을 보장합니다.
    return """
CREATE INDEX IF NOT EXISTS day23_search_docs_embedding_hnsw_idx
ON day23_search_docs
USING hnsw (embedding vector_cosine_ops);
""".strip()
# END D23-06-B01


# BEGIN D23-06-B02
def explain_sql():
    """
    TODO D23-06-B02 · explain_sql
        SELECT id FROM day23_search_docs를 거리순으로 검색하는
        EXPLAIN (ANALYZE, BUFFERS) SQL을 작성하세요. 바인딩은 %s 두 개.
        인덱스 사용 여부를 임의로 주장하면 안 됩니다.
    """
    # [핵심 포인트 2: EXPLAIN (ANALYZE, BUFFERS) 기반 실제 실행 계획 및 버퍼 접근량 조회]
    # - run() 내부에서 conn.execute(sql_plan, (E5_MODEL_ID, qvec)) 형태로 %s 2개를 바인딩합니다.
    # - 첫 번째 %s는 WHERE embedding_model = %s, 두 번째 %s는 ORDER BY embedding <=> %s ASC에 대응됩니다.
    return """
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM day23_search_docs
WHERE embedding_model = %s
ORDER BY embedding <=> %s ASC
LIMIT 3;
""".strip()
# END D23-06-B02


# BEGIN D23-06-B03
def read_scan_type(plan_lines):
    """
    TODO D23-06-B03 · read_scan_type
        PostgreSQL EXPLAIN 텍스트에서 Index Scan / Seq Scan / 기타를 구분하세요.
        계획이 없으면 unknown, index가 있으면 index, seq면 seq로 반환합니다.
        작은 9건 테이블에서 Seq Scan은 오류가 아닙니다.
    """
    # [핵심 포인트 3: EXPLAIN 출력 텍스트 파싱을 통한 스캔 방식(index / seq / unknown) 판별]
    # - 실행 계획 줄 목록이 비어 있으면 'unknown'을 반환합니다.
    # - 'Index Scan'(또는 'Index Only Scan', 'Bitmap Index Scan')이 감지되면 'index',
    #   'Seq Scan'이 감지되면 'seq'를 반환하여 실제 옵티마이저의 선택을 객관적으로 기록합니다.
    if not plan_lines:
        return "unknown"
    plan_text = " ".join(str(line) for line in plan_lines).lower()
    if not plan_text.strip():
        return "unknown"
    if "index" in plan_text:
        return "index"
    if "seq scan" in plan_text or "seq" in plan_text:
        return "seq"
    return "unknown"
# END D23-06-B03


def run(mode, level, args):
    sql_index = create_index_sql()
    sql_plan = explain_sql()
    result = dict(
        exercise=6,
        level=level,
        source_mode="simulated" if mode == "fixture" else "pgvector_live",
        index_sql=sql_index,
        explain_sql=sql_plan,
    )
    if mode == "fixture":
        sample = [
            "Seq Scan on day23_search_docs (cost=...)",
            "Sort Key: (embedding <=> ...)",
        ]
        result["scan_type"] = read_scan_type(sample)
        result["plan_is_simulated"] = True
    else:
        encoder = get_encoder("live")
        qvec = encode_question(encoder, "서버는 어디에서 실행하나요?")
        with connect_db(Path(__file__).with_name(".env")) as conn:
            check_data_ready(conn)
            if getattr(args, "create_index", False):
                conn.execute(sql_index)
                conn.execute("ANALYZE day23_search_docs")
            plan_lines = [
                str(r[0])
                for r in conn.execute(sql_plan, (E5_MODEL_ID, qvec)).fetchall()
            ]
            result["scan_type"] = read_scan_type(plan_lines)
            result["explain_lines"] = plan_lines
            if level >= 3:
                # Exact 기준선과 인덱스 유도 계획을 같은 질문/데이터/필터에서 실제 비교합니다.
                # SET LOCAL은 수업용 트랜잭션 동안만 적용되며 결과의 우열을 단정하지 않습니다.
                conn.execute("SET LOCAL enable_indexscan=off")
                conn.execute("SET LOCAL enable_bitmapscan=off")
                exact_ids = [
                    h["id"]
                    for h in exact_topk(
                        conn, qvec, k=3, category="development"
                    )
                ]
                conn.execute("SET LOCAL enable_indexscan=on")
                conn.execute("SET LOCAL enable_bitmapscan=on")
                conn.execute("SET LOCAL enable_seqscan=off")
                indexed_plan = [
                    str(r[0])
                    for r in conn.execute(
                        sql_plan, (E5_MODEL_ID, qvec)
                    ).fetchall()
                ]
                indexed_ids = [
                    h["id"]
                    for h in exact_topk(
                        conn, qvec, k=3, category="development"
                    )
                ]
                conn.execute("SET LOCAL enable_seqscan=on")
                confirmed_index = read_scan_type(indexed_plan) == "index"
                result["comparison"] = {
                    "category": "development",
                    "k": 3,
                    "exact_ids": exact_ids,
                    "forced_plan_ids": indexed_ids,
                    "forced_plan_scan": read_scan_type(indexed_plan),
                    "hnsw_index_observed": confirmed_index,
                    "exact_vs_ann_overlap": (
                        compare_topk(exact_ids, indexed_ids)
                        if confirmed_index
                        else None
                    ),
                    "note": "Index Scan이 관측됐을 때만 ANN 비교라 기록합니다. 9건에서 속도 향상 주장 금지.",
                }
    if level >= 2:
        result["operator_compatible"] = check_operator_compatibility(
            sql_plan, "vector_cosine_ops"
        )
        result["example_overlap"] = compare_topk(
            [102, 106, 107], [102, 107, 101]
        )
    if level >= 3:
        result["ann_filtered_example"] = filtered_ann_warning(
            k=3, returned=1, exact_count=4
        )
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 06 · Exact·HNSW·EXPLAIN"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )

    parser.add_argument(
        "--create-index",
        action="store_true",
        help="live에서만 HNSW 인덱스를 실제 생성",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_06.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()