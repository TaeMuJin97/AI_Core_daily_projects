"""
==============================================================================
[실습 보고서: Day 23 실습 01 - 검색 대상 데이터 계약 및 E5 passage 입력 조립 (main.py)]
1. 실험 목적:
   - Day 21~22에서 수동으로 고르던 지식 스냅샷(101~103)을 벡터 검색(Semantic Search) 파이프라인에
     연결하기에 앞서, 원본 데이터의 ID·본문 불변성과 E5 모델의 입력 접두어 규약을 검증함.
2. 핵심 아키텍처 개념:
   - 고정 기준선(Baseline Snapshot) 유지 (D23-01-B01):
     104~109번 확장 자료가 추가되더라도, 기존 평가 기준인 101·102·103번의 원문(id/title/content)을
     수정하거나 덮어쓰지 않고 정확히 추출해야 이전 차시와의 비교가 가능함.
   - 비대칭 검색(Asymmetric Search) 입력 계약 (D23-01-B02):
     intfloat/multilingual-e5-small 모델은 짧은 질문('query: ')과 긴 지식 본문('passage: ')을
     구분하여 학습되었으므로, DB에 저장할 지식 텍스트는 반드시 'passage: {title} {content}' 형태로 구성함.
   - 원문-벡터 추적 매핑 (D23-01-B03):
     임베딩 벡터만으로는 사용자에게 근거를 설명할 수 없으며, 원문이나 모델 버전이 바뀌었을 때
     재임베딩 여부를 판단하기 위해 id·원문·category·source_version·passage_input을 함께 기록함.
==============================================================================
"""
"""Day23 실습 01 · 검색 대상과 ID (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from day23kit.data import load_knowledge
from day23kit.io import save_result


# BEGIN D23-01-B01
def select_original(rows):
    """
    TODO D23-01-B01 · select_original
        기존 수업에서 사용한 101·102·103만 ID 오름차순으로 선택합니다.
        입력: 전체 지식 목록(list[dict]). 출력: 원래 지식 3개를 담은 list.
        원본 딕셔너리의 id/title/content를 수정하지 마세요.
        개념: 원문 ID 고정·검색할 자료의 범위.
    """
    # [핵심 포인트 1: 기존 스냅샷 ID(101, 102, 103) 필터링 및 오름차순 정렬]
    # - 원본 딕셔너리 객체를 변경하지 않고 조건에 맞는 항목만 골라 id 기준 오름차순 정렬합니다.
    target_ids = {101, 102, 103}
    selected = [r for r in rows if r.get("id") in target_ids]
    return sorted(selected, key=lambda r: r["id"])
# END D23-01-B01


# BEGIN D23-01-B02
def make_passage_input(row):
    """
    TODO D23-01-B02 · make_passage_input
        E5 문서 입력 텍스트를 "passage: 제목 본문" 형식으로 만드세요.
        입력: 지식 한 행. 출력: 문자열. 제목과 본문을 공백 하나로 구분하세요.
        개념: FAQ 질문과 달리 지식 본문을 검색 대상으로 사용합니다.
    """
    # [핵심 포인트 2: E5 모델 비대칭 검색용 passage 접두어 조립]
    # - 질문(query:)과 달리 검색 대상 문서 본문에는 반드시 "passage: " 접두어를 붙입니다.
    return "passage: " + row["title"] + " " + row["content"]
# END D23-01-B02


# BEGIN D23-01-B03
def make_mapping(rows):
    """
    TODO D23-01-B03 · make_mapping
        각 지식의 id/title/content/category/source_version 및 passage_input을 기록하세요.
        입력: 선택된 지식 목록. 출력: 딕셔너리 목록.
        개념: 벡터를 생성하기 전에도 원문·ID·버전을 추적해야 합니다.
    """
    # [핵심 포인트 3: 임베딩 전 원문 메타데이터 및 실제 모델 입력 문자열 대응표 생성]
    # - 추후 벡터와 원문의 1:1 매핑 검증 및 버전 변경 추적을 위해 필수 5개 필드와 passage_input을 함께 묶습니다.
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "content": r["content"],
            "category": r["category"],
            "source_version": r["source_version"],
            "passage_input": make_passage_input(r),
        }
        for r in rows
    ]
# END D23-01-B03


def run(mode, level, args):
    rows = load_knowledge()
    selected = select_original(rows)
    passage = make_passage_input(selected[1])
    mapping = make_mapping(selected if level == 1 else rows)
    result = dict(
        exercise=1,
        level=level,
        source_mode="local_snapshot",
        selected_ids=[r["id"] for r in selected],
        example_passage=passage,
        total_mapped=len(mapping),
        mapping=mapping,
    )
    if level >= 2:
        result["unique_ids"] = len(reject_duplicate_ids(rows))
        result["all_fields_valid"] = reject_missing_fields(rows)
    if level >= 3:
        result["versions"] = audit_versions(rows)
    return result


def main():
    parser = argparse.ArgumentParser(description="Day23 실습 01 · 검색 대상과 ID")
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_01.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()