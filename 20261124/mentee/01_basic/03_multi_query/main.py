"""Day27 강의 실습. 실행은 역할 폴더에서 Python으로 실행합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROLE_ROOT = next(p for p in HERE.parents if (p / "coursekit").is_dir())
sys.path.insert(0, str(ROLE_ROOT))

import argparse
from langchain_core.documents import Document  # 병합 후 새 메타데이터(found_by_query)를 담을 객체
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report


def plan_queries(base: str, extras: list[str], limit: int = 2) -> list[str]:
    """원 질문을 포함한 서로 다른 질문 2개로 시작합니다."""
    # BEGIN D27-03-B01
    # [흐름 이해: 검색할 Multi-query 목록 확정하기]
    # 1) 원래 질문(base)은 검색 의도의 기준이므로 반드시 첫 번째 항목으로 넣습니다.
    # 2) base가 비어 있거나 limit이 1 미만이면 잘못된 입력이므로 ValueError로 즉시 차단합니다.
    # 3) [base, *extras] 순서대로 공백을 정리(strip)하면서 이미 담긴 질문과 중복되지 않는 것만 골라
    #    기본필수 기준인 서로 다른 질문 2개(limit=2)까지 채워 반환합니다.
    if not isinstance(base, str) or not base.strip():
        raise ValueError("기본 질문(base)은 비어 있을 수 없습니다.")
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit은 1 이상의 정수여야 합니다.")

    unique_queries: list[str] = []
    for candidate in [base, *(extras or [])]:
        if not isinstance(candidate, str):
            continue
        cleaned = candidate.strip()
        if cleaned and cleaned not in unique_queries:
            unique_queries.append(cleaned)
        if len(unique_queries) >= limit:
            break

    return unique_queries
    # END D27-03-B01


def merge_candidates(pairs: list[tuple[str, list[Document]]]) -> list[Document]:
    """chunk_id를 중복 제거 키로 사용하고 found_by_query를 Metadata에 기록합니다."""
    # BEGIN D27-03-B02
    # [흐름 이해: 여러 질의에서 찾아온 후보 Document를 chunk_id 기준으로 통합하기]
    # - 입력 pairs 구조: [(질의1, [Document, ...]), (질의2, [Document, ...])]
    # - 같은 chunk_id가 여러 질의에서 동시에 검색되더라도 Context에 두 번 넣을 이유가 없으므로
    #   처음 등장한 Document 1건만 유지합니다.
    # - 대신 '어느 질의들에서 이 청크가 발견되었는지' 추적할 수 있도록
    #   metadata["found_by_query"] 리스트에 해당 질의 문자열들을 순서대로 누적합니다.
    merged_by_chunk: dict[str, Document] = {}

    for query, docs in pairs:
        for doc in docs:
            # 필수 식별자인 chunk_id가 없으면 KeyError로 즉시 드러냅니다.
            chunk_id = doc.metadata["chunk_id"]

            if chunk_id not in merged_by_chunk:
                # 원본 Document.metadata를 직접 건드리지 않도록 딕셔너리를 복사해 새 Document 생성
                new_meta = {**doc.metadata, "found_by_query": [query]}
                merged_by_chunk[chunk_id] = Document(
                    page_content=doc.page_content,
                    metadata=new_meta,
                )
            else:
                found_list = merged_by_chunk[chunk_id].metadata["found_by_query"]
                if query not in found_list:
                    found_list.append(query)

    return list(merged_by_chunk.values())
    # END D27-03-B02


def main():
    # 1) 실행 옵션 파싱 (--offline: 고정 예시 / 생략: CUDA + E5 + PostgreSQL + LLM 실측 경로)
    parser = argparse.ArgumentParser(description="Day27 실습 03 · 03_multi_query")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    # 2) STAGE_RUNNERS[3]에 [plan_queries, merge_candidates] 주입 후 질의별 검색 및 병합 실행
    report = STAGE_RUNNERS[3](args.offline, [plan_queries, merge_candidates])

    # 3) 실행 모드에 따라 day27_03_fixture.json 또는 day27_03_live.json 저장
    path = save_report(
        HERE,
        "day27_03_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 03 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()