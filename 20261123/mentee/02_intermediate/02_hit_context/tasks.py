"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 찾도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent        # 현재 파일(tasks.py)이 있는 폴더
ROLE_ROOT = HERE.parents[1]                   # 두 단계 상위 폴더 (mentee 또는 mentor 루트)
sys.path.insert(0, str(ROLE_ROOT))            # Python 모듈 탐색 경로 맨 앞에 추가

from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record

# -----------------------------------------------------------------------------
# 2. 상수 정의 (Magic Number 제거!)
#    - 코드 곳곳에 숫자 2나 "\n\n"을 직접 적지 않고, 의미 있는 이름의 상수로 한 곳에 모읍니다.
#    - 파이썬 관례(PEP 8)상 바뀌지 않는 설정 상수는 대문자 스네이크 케이스(UPPER_SNAKE_CASE)로 적습니다.
# -----------------------------------------------------------------------------
DEFAULT_MAX_ITEMS: int = 2   # 기본으로 Context에 포함할 최대 문서(Hit) 개수
BLOCK_SEPARATOR: str = "\n\n"  # 문서 블록 사이를 구분할 빈 줄 하나


def format_hit(hit: dict) -> str:
    """Hit 한 건의 ID·위치·본문을 한 문자열 블록으로 반환합니다."""
    # BEGIN D26-02-I01
    # [1단계 역할: 단일 Hit 꾸미기]
    # 본문(body)만 넘기면 모델이 출처를 알 수 없으므로,
    # 맨 첫 줄에 "[정수ID] 원문위치" 이름표를 붙이고 줄바꿈(\n) 뒤 원문 전체를 이어 붙입니다.
    citation_id = hit["citation_id"]        # 답변 source_ids와 대조할 정수 ID (예: 201)
    source_locator = hit["source_locator"]  # 원문 파일·섹션 위치 (예: attendance_v2.md#sec-1)
    body = hit["body"]                      # 검색된 청크 원문 텍스트

    return f"[{citation_id}] {source_locator}\n{body}"
    # END D26-02-I01


def select_hits(hits: list[dict], max_items: int = DEFAULT_MAX_ITEMS) -> list[dict]:
    """입력 순서를 유지해 앞의 최대 max_items건만 고릅니다."""
    # BEGIN D26-02-I02
    # [2단계 역할: 후보 목록에서 실제 사용할 Hit만 추려내기]
    # - hits[:2]처럼 Magic Number를 직접 쓰지 않고, 매개변수 max_items를 사용합니다.
    # - 호출 시 max_items를 생략하면 상단의 DEFAULT_MAX_ITEMS(2)가 자동으로 적용됩니다.
    # - 방어 코드: max_items가 0 이하일 때 파이썬 음수 슬라이싱이 동작하지 않도록 빈 리스트 반환
    if max_items <= 0:
        return []

    return hits[:max_items]
    # END D26-02-I02


def make_context(
    hits: list[dict],
    max_items: int = DEFAULT_MAX_ITEMS,
) -> tuple[str, list[int]]:
    """선택한 목록에서 Context와 포함 ID를 동시에 만듭니다."""
    # BEGIN D26-02-I03
    # [3단계 역할: 조립기 (선택 → 포맷팅 → 연결 + 허용 ID 동시 수집)]
    # 1) 위에서 분리해 둔 select_hits()를 호출해 실제로 넣을 문서만 먼저 확정합니다.
    # 2) 확정된 selected_hits를 '같은 for 반복문'으로 돌면서
    #    - 모델 입력용 텍스트 블록(blocks)
    #    - 서버 검증용 허용 출처 ID(included_ids)
    #    두 가지를 동시에 모아야 모델이 읽은 문서와 허용 ID가 100% 일치합니다.
    # 3) 빈 리스트([])가 들어와도 blocks가 비어 있어 ""와 []를 안전하게 반환합니다.
    selected_hits = select_hits(hits, max_items=max_items)

    blocks: list[str] = []
    included_ids: list[int] = []

    for hit in selected_hits:
        blocks.append(format_hit(hit))            # 1단계 함수 재사용: 출처 포함 문자열 블록 생성
        included_ids.append(hit["citation_id"])   # 같은 Hit의 정수 citation_id 기록

    context = BLOCK_SEPARATOR.join(blocks)        # 블록 사이를 빈 줄("\n\n")로 연결
    return context, included_ids
    # END D26-02-I03


def main():
    # 1) 고정 예시 데이터(출석 v2, ID=201) 1건 로드
    hit = example_hit()

    # 2) make_context 내부에서 select_hits → format_hit 순서로 실행되어 Context와 included_ids 생성
    context, included_ids = make_context([hit])

    # 3) 결과 저장 (character_count는 단순 문자열 길이이며 LLM Token 수가 아님)
    report = {
        "execution": execution_record("local_python"),
        "context": context,
        "included_ids": included_ids,
        "input_source": "lecture_fixture",
        "character_count": len(context),
    }
    path = save_json(HERE, "hit_context.json", report)
    show_success("02 응용", path)


if __name__ == "__main__":
    main()