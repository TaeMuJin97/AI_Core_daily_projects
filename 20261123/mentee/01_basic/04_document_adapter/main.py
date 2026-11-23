"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent        # 현재 파일(main.py)이 위치한 폴더 (04_document_adapter)
ROLE_ROOT = HERE.parents[1]                   # 두 단계 상위 폴더 (mentee 또는 mentor 루트)
sys.path.insert(0, str(ROLE_ROOT))            # Python 모듈 탐색 경로 맨 앞에 추가

from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record
from langchain_core.documents import Document  # LangChain의 표준 문서 데이터 객체(택배 상자)
import argparse

# -----------------------------------------------------------------------------
# 2. 오늘의 최소 Metadata 계약 (Magic String 중복 방지용 상수 튜플)
#    - 이 6개 필드는 답변 출처를 원문까지 역추적하기 위한 필수 신분증입니다.
#    - 여섯 값 모두 입력 Hit에서 그대로 가져오며, 임의로 추가하거나 타입을 바꾸지 않습니다.
# -----------------------------------------------------------------------------
METADATA_KEYS = (
    "citation_id",     # 답변 source_ids와 대조할 정수 ID (int 유지 필수!)
    "chunk_id",        # 청크 중복 제거용 문자열 ID
    "doc_id",          # 문서 식별자 (예: DOC-ATTEND)
    "source_version",  # 문서 버전 (예: v2)
    "source_locator",  # 실제 원문 파일·위치 (예: attendance_v2.md#sec-1)
    "category",        # 검색 범위를 나눈 분류 (예: 학사)
)


def to_document(hit: dict) -> Document:
    """한 Hit의 본문과 여섯 Metadata 값을 Document로 옮깁니다."""
    # BEGIN D26-04-B01
    # [흐름 이해: 기존 Hit(dict) → LangChain 표준 Document 객체로 변환]
    # 1) 본문(hit["body"])은 Document의 'page_content' 자리에 그대로 담습니다.
    # 2) 출처 6개 필드는 'metadata' 딕셔너리에 그대로 옮겨 담습니다.
    #
    # ※ 왜 hit.get(key)가 아니라 hit[key]를 쓰는가?
    #    - source_locator 같은 필수 출처가 빠졌을 때 None으로 조용히 넘어가면 출처 추적이 깨집니다.
    #    - hit[key]를 써야 필수 값이 없을 때 즉시 KeyError를 발생시켜 문제를 바로 잡을 수 있습니다!
    # ※ 주의: citation_id를 str()로 바꾸지 말고 원래의 int 타입 그대로 유지합니다.
    metadata = {key: hit[key] for key in METADATA_KEYS}

    return Document(
        page_content=hit["body"],  # 모델이 읽을 실제 청크 본문
        metadata=metadata,         # 서버가 출처 연결·검증에 쓸 6개 메타데이터
    )
    # END D26-04-B01


def hits_to_documents(hits: list[dict]) -> list[Document]:
    """순서대로 변환한 Document 목록을 반환합니다. 빈 입력은 빈 목록입니다."""
    # BEGIN D26-04-B02
    # [흐름 이해: 여러 건의 검색 결과(Hit 목록)를 순위(순서) 그대로 Document 목록으로 변환]
    # - 리스트 컴프리헨션으로 입력 hits의 순서를 유지하며 한 건씩 to_document()를 호출합니다.
    # - hits가 빈 리스트([])이면 가짜 문서를 만들지 않고 자연스럽게 빈 리스트([])를 반환합니다.
    return [to_document(hit) for hit in hits]
    # END D26-04-B02


def metadata_is_preserved(hit: dict, metadata: dict) -> bool:
    """제공된 관찰 함수: 여섯 필드가 모두 있고 각 값이 같은지 확인합니다."""
    required = {"citation_id", "chunk_id", "doc_id", "source_version", "source_locator", "category"}
    # 일부 필드만 복사한 결과를 '보존 완료'로 표시하지 않도록 Key 집합부터 확인합니다.
    return set(metadata) == required and all(metadata[key] == hit[key] for key in required)


def main():
    # 1) 실행 옵션 파싱: 기본은 오프라인 고정 예시, --live-db를 붙이면 실제 E5·PostgreSQL 검색
    parser = argparse.ArgumentParser(description="Hit → 실제 LangChain Document 변환")
    parser.add_argument("--live-db", action="store_true", help="실제 E5·PostgreSQL 검색 결과를 입력으로 사용")
    parser.add_argument("--question", default="15분 늦으면 어떻게 기록되나요?")
    parser.add_argument("--category", default="학사", choices=["학사", "시설", "지원"])
    parser.add_argument("--candidate-k", type=int, default=3)
    args = parser.parse_args()

    # 2) 입력 데이터(hits) 준비: 가짜(Fixture)든 진짜(DB)든 동일한 Hit 리스트 형태를 맞춥니다.
    if args.live_db:
        # --live-db를 선택한 경우에만 실제 모델·DB 준비 함수를 불러옵니다. (지연 import)
        from coursekit.live import make_search_hits
        search_hits = make_search_hits()
        hits = search_hits(args.question, args.category, k=args.candidate_k)
        mode, input_source = "live_db", "E5_PostgreSQL"
    else:
        hits = [example_hit()]
        mode, input_source = "local_adapter", "lecture_fixture"

    # 3) 핵심 어댑터 실행: Hit 목록 → LangChain Document 목록 변환
    documents = hits_to_documents(hits)

    # 4) 변환 전(hit)과 변환 후(doc)를 1:1로 비교해 손실·타입 변질 여부를 기록합니다.
    comparisons = []
    for hit, doc in zip(hits, documents):
        comparisons.append({
            "citation_id": doc.metadata["citation_id"],
            "body_preserved": doc.page_content == hit["body"],              # 본문이 100% 같은지
            "metadata_preserved": metadata_is_preserved(hit, doc.metadata), # 6개 키·값이 모두 같은지
            "citation_id_type": type(doc.metadata["citation_id"]).__name__, # "int" 유지 여부
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        })

    # 5) 최종 실행 결과 JSON 저장 (db/embedding 실제 사용 여부는 args.live_db에 따라 자동 기록)
    report = {
        "execution": execution_record(mode, db=args.live_db, embedding=args.live_db),
        "input_source": input_source,
        "input_count": len(hits),
        "document_count": len(documents),
        "documents": comparisons,
    }
    path = save_json(HERE, "document_adapter.json", report)
    show_success("04 기본필수", path)


if __name__ == "__main__":
    main()