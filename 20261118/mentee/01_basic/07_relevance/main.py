"""
==============================================================================
[실습 보고서: Day 23 실습 07 - 검색 결과 정성평가 및 근거 충분성 검토 (main.py)]
1. 실험 목적:
   - pgvector의 Top-k 검색이 반환한 후보 문서들을 대상으로, 벡터 거리(Cosine Distance)의 작음과
     실제 질문에 답할 수 있는 '근거 충분성(Relevance / Evidence Sufficiency)'이 별개임을 검증함.
2. 핵심 아키텍처 개념:
   - 고정 평가 케이스북(Casebook) 설계 (D23-07-B01):
     1) server ('서버는 어디에서 실행하나요?') -> 102번에 명확한 실행 위치 근거 존재
     2) retention ('실습 파일은 얼마나 보관하나요?') -> 101번이 '실습 파일 보관' 주제는 맞으나,
        '보관 위치(workspace)'만 있을 뿐 '보관 기간(얼마나)'에 대한 정보가 없음 (부분 관련 / 근거 부족)
     3) error ('오류 질문에는 무엇을 함께 적어야 하나요?') -> 103번/108번에 재현 정보·로그 근거 존재
   - 수동 기준표(Gold Reference)와 모델 점수 분리 (D23-07-B02):
     유사도/거리 임계값(Threshold)만으로 정답 여부를 자동 단정하지 않고, 원문 대조를 통한
     '관련 / 부분 관련 / 무관' 라벨로 검색 품질을 정성 평가함.
   - 거리(Distance)의 비확률적 해석 및 사람 검토(Human-in-the-loop) (D23-07-B03):
     LIMIT k는 DB에 있는 문서 중 상대적으로 가장 가까운 k개를 무조건 반환할 뿐이므로,
     distance 수치를 정답 확률(%)로 오해하지 않고 human_reviewed=False 상태에서 원문을 직접 대조함.
==============================================================================
"""
"""Day23 실습 07 · 검색 결과 정성평가 (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from day23kit.fixtures import fixture_search
from day23kit.embedding import get_encoder, encode_question
from day23kit.db import connect_db, exact_topk, check_data_ready
from day23kit.io import save_result


# BEGIN D23-07-B01
def make_casebook():
    """
    TODO D23-07-B01 · make_casebook
        강의의 질문 3종과 확인할 지식 ID를 구성하세요.
        server(102), retention(101: 보관 기간 없음), error(103/108).
        자동 생성한 정답이 아니라 사람이 평가할 고정 기준 샘플임을 표시합니다.
    """
    # [핵심 포인트 1: 정성평가를 위한 3대 대표 질문 케이스북 구성]
    # - 모델이 자동 생성한 정답이 아니라 사람이 원문을 읽고 대조할 고정 기준 샘플(human_curated_sample)임을 명시합니다.
    # - 특히 'retention' 케이스는 어휘적/주제적으로 가장 가까운 101번이 검색되더라도 실제 질문 의도인
    #   '보관 기간' 정보가 빠져 있는 대표적인 '검색 성공 ≠ 답변 가능 근거' 사례입니다.
    return [
        {
            "case_id": "server",
            "question": "서버는 어디에서 실행하나요?",
            "reference_ids": [102],
            "note": "102번 원문에 프로젝트 폴더에서 실행한다는 직접 근거 존재",
            "reference_origin": "human_curated_sample",
        },
        {
            "case_id": "retention",
            "question": "실습 파일은 얼마나 보관하나요?",
            "reference_ids": [101],
            "note": "101번은 보관 폴더(workspace)만 설명하며 보관 기간 정보는 없음",
            "reference_origin": "human_curated_sample",
        },
        {
            "case_id": "error",
            "question": "오류 질문에는 무엇을 함께 적어야 하나요?",
            "reference_ids": [103, 108],
            "note": "103번(코드와 오류 메시지) 및 108번(재현 순서·입력·출력·오류 전문) 관련",
            "reference_origin": "human_curated_sample",
        },
    ]
# END D23-07-B01


# BEGIN D23-07-B02
def judge_training_reference(case_id, doc_id):
    """
    TODO D23-07-B02 · judge_training_reference
        교안에 미리 주어진 원문 근거로 관련/부분 관련/무관을 수동 기준표로 판정하세요.
        server:102 관련,106 부분 관련. retention:101 부분 관련(기간 없음).
        error:103,108 관련. 그 밖에는 무관.
        *이 표는 사람이 만든 교육용 기준이며 모델 검색 평가점수가 아닙니다.*
    """
    # [핵심 포인트 2: 원문 근거 기반 수동 판정 기준표(Gold Standard) 매핑]
    # - 벡터 유사도 점수가 아니라 사람이 원문 텍스트를 읽고 사전 정의한 교육용 기준표입니다.
    # - retention 케이스의 101번은 주제는 겹치나 핵심 정답(보관 기간)이 없으므로 '부분 관련'으로 분류합니다.
    gold = {
        "server": {102: "관련", 106: "부분 관련"},
        "retention": {101: "부분 관련"},
        "error": {103: "관련", 108: "관련"},
    }
    return gold.get(case_id, {}).get(int(doc_id), "무관")
# END D23-07-B02


# BEGIN D23-07-B03
def make_review_row(case, hit):
    """
    TODO D23-07-B03 · make_review_row
        질문 ID·검색된 ID·본문·거리·교재 기준 라벨을 한 행으로 만드세요.
        distance는 정답 확률로 표현하지 않습니다.
        human_reviewed는 False로 두어 실제 수강생의 근거 검토 전임을 표시합니다.
    """
    # [핵심 포인트 3: 거리(distance)와 원문(content)을 나란히 대조하는 리뷰 레코드 생성]
    # - distance는 벡터 공간에서의 상대적 코사인 거리일 뿐 정답 확률이 아닙니다.
    # - 코드 실행만으로 사람이 검토 완료했다고 위조하지 않도록 human_reviewed=False로 고정합니다.
    case_id = case["case_id"]
    doc_id = int(hit["id"])
    return dict(
        case_id=case_id,
        question=case["question"],
        retrieved_id=doc_id,
        content=hit["content"],
        distance=round(float(hit["distance"]), 6),
        training_reference_label=judge_training_reference(case_id, doc_id),
        human_reviewed=False,
    )
# END D23-07-B03


def run(mode, level, args):
    cases = make_casebook()
    reviews = []
    search_state = []
    for case in cases:
        # 검색 자체는 fixture의 수학 예시 또는 실제 E5/pgvector.
        if mode == "fixture":
            hits = fixture_search(case["question"], k=3)
        else:
            if "_live_cache" not in locals():
                encoder = get_encoder("live")
                conn = connect_db(Path(__file__).with_name(".env"))
                check_data_ready(conn)
                _live_cache = True
            qvec = encode_question(encoder, case["question"])
            hits = exact_topk(conn, qvec, 3)
        search_state.append(
            {
                "case_id": case["case_id"],
                "state": (
                    classify_search_state(hits)
                    if level >= 2
                    else ("candidates" if hits else "empty")
                ),
            }
        )
        for hit in hits:
            row = make_review_row(case, hit)
            row["source_version"] = hit["source_version"]
            reviews.append(row)
    result = dict(
        exercise=7,
        level=level,
        source_mode="simulated" if mode == "fixture" else "pgvector_exact",
        review_rows=reviews,
        search_states=search_state,
        human_evidence_ok=None,
    )
    if level >= 2:
        if mode == "live":
            qvec = encode_question(encoder, "서버는 어디에서 실행하나요?")
            baseline = [h["id"] for h in exact_topk(conn, qvec, k=3)]
            filtered = [
                h["id"]
                for h in exact_topk(
                    conn, qvec, k=3, category="development"
                )
            ]
        else:
            baseline = [
                h["id"]
                for h in fixture_search("서버는 어디에서 실행하나요?", k=3)
            ]
            filtered = [
                h["id"]
                for h in fixture_search(
                    "서버는 어디에서 실행하나요?", k=3, category="development"
                )
            ]
        result["filter_effect"] = review_filter_effect(baseline, filtered)
        result["empty_is_not_error"] = (
            classify_search_state([]) == "empty"
            and classify_search_state([], error="DB 연결 오류") == "error"
        )
    if level >= 3:
        result["evaluation_integrity"] = check_evaluation_integrity(reviews)
    if mode == "live":
        conn.close()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 07 · 검색 결과 정성평가"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_07.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()

# ==============================================================================
# 20261118 07_relevance
# outputs/exercise_07.json 검토 결과
# - 현재 생성되는 값에서는 Top-k(k=3)가 상대적으로 가장 가까운 3건을 무조건 반환할 뿐이며,
#   distance 수치만으로는 두 벡터가 질문의 정답 근거를 포함할 만큼 유사하다는 근거가 부족하다.
# - 특히 'retention(실습 파일은 얼마나 보관하나요?)' 케이스에서는 101번 문서('실습 파일은
#   workspace 폴더에 보관합니다')가 1순위로 검색되나, 보관 위치만 있을 뿐 보관 기간 정보가
#   누락되어 있어('부분 관련') 답변 근거로 사용할 수 없다.
# - 따라서 근거 부족(insufficient_context) 상태를 분리해 처리하고, 보관 기간 및 삭제 정책이
#   명시된 추가 데이터를 적재하는 것을 고려해야 한다.
# ==============================================================================