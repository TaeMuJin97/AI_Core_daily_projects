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
import math
from langchain_core.documents import Document
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report


def create_pairs(question: str, docs: list[Document]) -> list[tuple[str, str]]:
    """CrossEncoder 입력은 [질문, 문서본문]의 쌍 목록입니다."""
    # BEGIN D27-05-B01
    # [흐름 이해: Bi-Encoder와 다른 Cross-Encoder만의 입력 쌍 만들기]
    # - Bi-Encoder(E5)는 질문과 문서를 각각 따로 벡터로 바꾸지만,
    #   Cross-Encoder는 (질문, 문서 본문) 두 텍스트를 한 쌍으로 묶어 동시에 읽고 관련성을 채점합니다.
    # - 질문이 비어 있으면 즉시 ValueError를 내고, docs가 비어 있으면 빈 리스트를 반환합니다.
    if not isinstance(question, str) or not question.strip():
        raise ValueError("질문(question)은 비어 있을 수 없습니다.")

    if not docs:
        return []

    clean_q = question.strip()
    pairs: list[tuple[str, str]] = []
    for doc in docs:
        if not isinstance(doc, Document):
            raise TypeError("docs의 모든 원소는 LangChain Document여야 합니다.")
        pairs.append((clean_q, doc.page_content))

    return pairs
    # END D27-05-B01


def rank_documents(question: str, docs: list[Document], scorer) -> list[Document]:
    """Reranker는 후보를 새로 찾지 않고 동일 후보를 순위 변경합니다."""
    # BEGIN D27-05-B02
    # [흐름 이해: 점수 계산 → 유효성 검증 → 내림차순 재정렬 → 메타데이터 보존]
    # 1) 후보(docs)가 비어 있으면 모델 호출 없이 빈 리스트를 반환합니다.
    # 2) create_pairs()로 (질문, 본문) 쌍을 만든 뒤 scorer(pairs)로 관련성 점수를 계산합니다.
    #    (※ 이 점수는 '정답 확률(%)'이 아니라 상대적인 순위 판단용 모델 점수입니다.)
    # 3) 점수 개수가 후보 수와 일치하는지, 모든 점수가 유한한 실수(NaN/Inf 아님)인지 검사합니다.
    # 4) 점수가 높은 순서(reverse=True)로 정렬하되, 원본 metadata(chunk_id, citation_id 등)는
    #    그대로 유지하면서 rerank_score만 추가한 새 Document 목록을 반환합니다.
    if not docs:
        return []

    pairs = create_pairs(question, docs)
    raw_scores = list(scorer(pairs))

    if len(raw_scores) != len(docs):
        raise ValueError(f"점수 개수({len(raw_scores)})와 후보 문서 수({len(docs)})가 일치하지 않습니다.")

    scores: list[float] = []
    for s in raw_scores:
        val = float(s)
        if not math.isfinite(val):
            raise ValueError(f"유효하지 않은 rerank 점수입니다: {s!r}")
        scores.append(val)

    scored_docs: list[Document] = []
    for score, doc in zip(scores, docs):
        new_meta = {**doc.metadata, "rerank_score": score}
        scored_docs.append(
            Document(
                page_content=doc.page_content,
                metadata=new_meta,
            )
        )

    # 점수 내림차순 정렬 (후보 밖의 새 문서를 추가하지 않고 기존 후보의 순서만 재배치)
    ranked_docs = sorted(
        scored_docs,
        key=lambda d: float(d.metadata["rerank_score"]),
        reverse=True,
    )
    return ranked_docs
    # END D27-05-B02


def main():
    # 1) 실행 옵션 파싱 (--offline: 고정 점수 예시 / 생략: RTX 5080 CUDA Cross-Encoder 실측)
    parser = argparse.ArgumentParser(description="Day27 실습 05 · 05_cross_encoder_reranking")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    # 2) STAGE_RUNNERS[5]에 [create_pairs, rank_documents] 주입 후 실행
    report = STAGE_RUNNERS[5](args.offline, [create_pairs, rank_documents])

    # 3) 실행 모드에 따라 day27_05_fixture.json 또는 day27_05_live.json 저장
    path = save_report(
        HERE,
        "day27_05_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 05 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()