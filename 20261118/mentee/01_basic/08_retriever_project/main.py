"""
==============================================================================
[실습 보고서: Day 23 실습 08 - AI Agent용 Semantic Search Retriever 파이프라인 (main.py)]
1. 실험 목적:
   - 1~7교시에서 구현한 질문 입력 검증, E5 Query 임베딩, pgvector Exact Top-k 검색,
     표준 후보 포맷팅을 하나의 재사용 가능한 Retriever 인터페이스로 통합함.
   - 추후 Day 25 RAG 파이프라인에서 Context Builder 및 LLM 답변 생성기가 호출할 수 있는
     깔끔한 입출력 데이터 계약을 확립함.
2. 핵심 아키텍처 개념:
   - 순수 함수 기반 입력 검증 (D23-08-B01):
     무거운 임베딩 모델이나 DB 커넥션을 호출하기 전에, 빈 질문이나 공백만 있는 입력을
     가장 앞단에서 즉시 차단(Fail-Fast)하여 불필요한 연산과 가짜 벡터 생성을 방지함.
   - 예외 은닉 금지 및 실행 경로 분리 (D23-08-B02):
     오프라인 테스트용 fixture 경로와 실제 E5 + PostgreSQL live 경로를 분리하되,
     live 모드에서 DB 연결 실패나 테이블 미준비 예외가 발생했을 때 이를 빈 리스트([])로
     삼키지 않고 상위로 그대로 전파하여 '검색 결과 없음(empty)'과 '시스템 장애(error)'를 구분함.
   - 원문 불변성 및 역할 경계 준수 (D23-08-B03):
     Retriever의 책임은 질문과 가까운 후보 원문(id, title, content, category, source_version)과
     거리(distance)를 왜곡 없이 전달하는 것까지이며, 원문을 임의로 요약하거나 답변 성공 여부(answered)를
     스스로 단정하지 않음.
==============================================================================
"""
"""Day23 실습 08 · AI Agent용 Retriever (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from time import perf_counter
from day23kit.fixtures import fixture_search
from day23kit.embedding import get_encoder, encode_question
from day23kit.db import connect_db, exact_topk, check_data_ready
from day23kit.io import save_result


# BEGIN D23-08-B01
def validate_question(question):
    """
    TODO D23-08-B01 · validate_question
        질문은 1자 이상의 문자열이어야 하며 앞뒤 공백을 제거하세요.
        빈 값/공백만 있는 값이면 ValueError. 반환은 정리된 질문.
        API가 연결되어 있지 않아도 검사 가능한 순수 함수입니다.
    """
    # [핵심 포인트 1: 외부 API/DB 의존성 없는 순수 입력 검증 함수]
    # - 문자열 타입이 아니거나 strip() 이후 길이가 0이면 즉시 ValueError를 발생시킵니다.
    if not isinstance(question, str):
        raise ValueError("질문은 문자열(str)이어야 합니다.")
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("질문은 공백을 제외한 1자 이상의 문자열이어야 합니다.")
    return cleaned
# END D23-08-B01


# BEGIN D23-08-B02
def retrieve_candidates(question, mode, k, category, env_file):
    """
    TODO D23-08-B02 · retrieve_candidates
        fixture면 교육용 fixture_search, live면 E5 query Embedding → pgvector Exact SQL을 사용하세요.
        실제 live는 exercise05에서 9개 자료를 먼저 저장해야 합니다.
        DB 연결 실패를 빈 결과 []로 바꾸지 말고 예외를 전달하세요.
    """
    # [핵심 포인트 2: fixture / live 검색 실행 경로 분기 및 DB 예외 투명 전파]
    # - fixture 모드에서는 오프라인 시뮬레이션 검색 결과를 반환합니다.
    # - live 모드에서는 E5 모델로 질문을 인코딩('query: ' 접두어 포함)한 뒤,
    #   PostgreSQL day23_search_docs 테이블에 대해 Exact Top-k 검색을 수행합니다.
    # - DB 연결 실패 등을 try/except로 잡아 []로 둔갑시키면 장애를 정상 빈 결과로 오인하므로 예외를 그대로 둡니다.
    cleaned_q = validate_question(question)
    if mode == "fixture":
        return fixture_search(cleaned_q, k=k, category=category)

    encoder = get_encoder("live")
    qvec = encode_question(encoder, cleaned_q)
    with connect_db(env_file) as conn:
        check_data_ready(conn)
        return exact_topk(conn, qvec, k=k, category=category)
# END D23-08-B02


# BEGIN D23-08-B03
def format_candidates(hits):
    """
    TODO D23-08-B03 · format_candidates
        후보의 id/title/content/category/source_version/distance를 반환하세요.
        검색된 원문을 요약·변조하지 않고, distance는 숫자 그대로 둡니다.
        답변 상태(answered)를 자동으로 부여하지 마세요.
    """
    # [핵심 포인트 3: Context 후보 전달을 위한 6대 표준 필드 직렬화]
    # - 검색된 원문(title, content)을 변조하지 않고 메타데이터(id, category, source_version)와
    #   수치형 거리(distance)만 정확히 담아 다음 단계(Context 조립기)로 넘깁니다.
    return [
        {
            "id": int(h["id"]),
            "title": h["title"],
            "content": h["content"],
            "category": h["category"],
            "source_version": h["source_version"],
            "distance": round(float(h["distance"]), 6),
        }
        for h in hits
    ]
# END D23-08-B03


def run(mode, level, args):
    question = validate_question(
        getattr(args, "question", "서버는 어디에서 실행하나요?")
    )
    k = 3 if level == 1 else args.k
    category = None if level == 1 else args.category
    if level >= 2:
        options = validate_options(k, category)
    else:
        options = {"k": k, "category": category}
    t0 = perf_counter()
    hits = retrieve_candidates(
        question,
        mode,
        options["k"],
        options["category"],
        Path(__file__).with_name(".env"),
    )
    elapsed = (perf_counter() - t0) * 1000
    formatted = format_candidates(hits)
    result = dict(
        exercise=8,
        level=level,
        source_mode="simulated" if mode == "fixture" else "pgvector_exact",
        question=question,
        options=options,
        retrieved=formatted,
        retrieved_count=len(formatted),
        human_evidence_ok=None,
        next_step="검토 후 Context 후보로 전달; LLM 답변 생성은 Day25 RAG에서 수행",
    )
    if level >= 2:
        result["run_report"] = make_run_report(question, hits, mode, elapsed)
    if level >= 3:
        result["contract_check"] = check_model_and_versions(hits, mode)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 08 · AI Agent용 Retriever"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )

    parser.add_argument(
        "--question", default="서버는 어디에서 실행하나요?", help="검색 질문"
    )
    parser.add_argument(
        "--k", type=int, default=3, help="반환할 최대 검색 후보 (1~9)"
    )
    parser.add_argument(
        "--category",
        default=None,
        choices=["course", "development", "support"],
        help="Metadata 분류 필터",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_08.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()