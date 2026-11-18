"""
==============================================================================
[실습 보고서: Day 23 실습 03 - Sentence Transformers 및 E5 문장 Embedding 생성 (main.py)]
1. 실험 목적:
   - intfloat/multilingual-e5-small 모델의 비대칭 검색(Asymmetric Search) 입력 계약에 맞춰
     문서('passage: ')와 질문('query: ') 문자열을 분리 조립하고, 384차원 정규화 벡터를 생성함.
2. 핵심 아키텍처 개념:
   - 역할별 접두어 분리 (D23-03-B01, D23-03-B02):
     E5 모델은 학습 시 질문과 본문의 역할을 구분하도록 설계되었으므로, 저장할 지식 본문에는
     'passage: {title} {content}', 사용자 검색 질문에는 'query: {question}'을 일관되게 부여함.
   - 빈 질문 방어 (Fail-Fast):
     공백이나 빈 문자열에 'query: '만 붙여 임베딩하면 의미 없는 벡터가 생성되어 엉뚱한 Top-k 후보를
     반환하므로 인코딩 전에 즉시 차단함.
   - 동일 인코더 및 정규화 계약 (D23-03-B03):
     문서 벡터와 질의 벡터는 반드시 동일한 모델 가중치와 정규화 설정(normalize_embeddings=True)으로
     인코딩해야 동일한 384차원 단위 구면(Unit Hypersphere) 위에서 Cosine 비교가 성립함.
==============================================================================
"""
"""Day23 실습 03 · E5 문장 Embedding (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
import numpy as np
from day23kit.data import load_knowledge, passage_text, E5_MODEL_ID
from day23kit.embedding import get_encoder
from day23kit.io import save_result


# BEGIN D23-03-B01
def make_passages(rows):
    """
    TODO D23-03-B01 · make_passages
        지식 목록을 E5 문서 입력 문자열 목록으로 변환하세요.
        문서에는 'passage: ' + 제목 + ' ' + 본문을 사용합니다.
        한 행마다 정확히 한 문자열을 만들어 순서를 유지하세요.
    """
    # [핵심 포인트 1: 지식 목록 순서 보존 및 E5 passage 포맷팅]
    # - day23kit.data.passage_text(row)는 'passage: {title} {content}' 규약을 생성합니다.
    # - 입력 rows의 행 순서가 곧 출력 임베딩 행렬(n, 384)의 행 인덱스와 1:1로 대응됩니다.
    return [passage_text(row) for row in rows]
# END D23-03-B01


# BEGIN D23-03-B02
def make_queries(questions):
    """
    TODO D23-03-B02 · make_queries
        질문 목록 각 요소 앞에 query: 공백을 붙이세요.
        출력: 입력과 동일한 순서의 문자열 리스트.
        빈 질문을 추가해 그럴듯한 벡터를 만들지 마세요.
    """
    # [핵심 포인트 2: 사용자 질문 검증 및 query 접두어 부착]
    # - 빈 질문이나 공백 문자열이 들어오면 그럴듯한 가짜 벡터가 만들어지지 않도록 즉시 예외 처리합니다.
    if not questions:
        raise ValueError("질문 목록이 비어 있습니다.")
    result = []
    for q in questions:
        if not isinstance(q, str) or not q.strip():
            raise ValueError("빈 질문은 Embedding 입력으로 사용할 수 없습니다.")
        result.append("query: " + q.strip())
    return result
# END D23-03-B02


# BEGIN D23-03-B03
def encode_both(encoder, passages, queries):
    """
    TODO D23-03-B03 · encode_both
        같은 Encoder에 문서와 질문을 나누어 encode하세요.
        반드시 normalize_embeddings=True, convert_to_numpy=True를 전달합니다.
        결과: (doc_vectors, query_vectors). 기본필수의 모의 모드와
        --mode live의 E5 실측을 구분하여 같은 API를 사용합니다.
    """
    # [핵심 포인트 3: 동일 Encoder 및 L2 정규화(normalize_embeddings=True) 적용]
    # - fixture 모드(SimulatedEncoder)와 live 모드(SentenceTransformer) 모두 동일한 encode 인터페이스를 따릅니다.
    docs = encoder.encode(
        passages,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    queries_vec = encoder.encode(
        queries,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return docs, queries_vec
# END D23-03-B03


def run(mode, level, args):
    rows = load_knowledge()[:3] if level == 1 else load_knowledge()
    encoder = get_encoder(mode)
    passages = make_passages(rows)
    questions = make_queries(["서버는 어디에서 실행하나요?"])
    docs, queries = encode_both(encoder, passages, questions)
    result = dict(
        exercise=3,
        level=level,
        source_mode="e5_live" if mode == "live" else "simulated",
        model_id=E5_MODEL_ID if mode == "live" else encoder.model_id,
        document_shape=list(docs.shape),
        query_shape=list(queries.shape),
        example_passage=passages[0],
        example_query=questions[0],
    )
    if level >= 2:
        result["alignment"] = verify_alignment(rows, docs)
        result["vectors_valid"] = check_shapes_vectors(docs, queries, len(rows))
    if level >= 3:
        result["model_contract"] = make_model_stamp(encoder, mode)
    return result


def main():
    parser = argparse.ArgumentParser(description="Day23 실습 03 · E5 문장 Embedding")
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_03.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()