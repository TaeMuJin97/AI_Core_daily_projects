"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널에서 실행해도 상위 폴더의 공통 모듈(coursekit)을 찾도록 연결
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent        # 현재 파일(main.py)이 위치한 폴더 (02_hit_context)
ROLE_ROOT = HERE.parents[1]                   # 두 단계 상위 폴더 (mentee 또는 mentor 루트)
sys.path.insert(0, str(ROLE_ROOT))            # Python이 모듈을 찾을 때 이 경로를 최우선으로 탐색

from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record


def format_hit(hit: dict) -> str:
    """Hit 한 건의 ID·위치·본문을 한 문자열 블록으로 반환합니다."""
    # BEGIN D26-02-B01
    # [흐름 이해]
    # 검색 결과 한 건(hit)은 파이썬 dict(이름표가 붙은 데이터 묶음) 형태입니다.
    # 본문(body)만 덜렁 모델에 넘기면 나중에 "어디서 보고 답했는지" 출처를 가리킬 수 없으므로,
    # 본문 맨 첫 줄에 [citation_id]와 원문 위치(source_locator)를 이름표처럼 붙여 하나의 블록으로 만듭니다.
    #
    # [출력 형태 예시]
    # [201] attendance_v2.md#sec-1
    # 수업 시작 후 15분까지 입실하면 지각으로 기록합니다. ...
    citation_id = hit["citation_id"]        # 모델과 서버가 근거를 가리킬 정수 ID (예: 201)
    source_locator = hit["source_locator"]  # 실제 원문 파일과 위치 (예: attendance_v2.md#sec-1)
    body = hit["body"]                      # 검색된 청크의 원문 텍스트 전체

    # f-string으로 첫 줄([ID] 위치)과 다음 줄(본문)을 줄바꿈(\n)으로 연결해 반환합니다.
    return f"[{citation_id}] {source_locator}\n{body}"
    # END D26-02-B01


def make_context(hits: list[dict], max_items: int = 2) -> tuple[str, list[int]]:
    """앞에서 최대 max_items건을 골라 Context와 같은 선택의 ID 목록을 반환합니다."""
    # BEGIN D26-02-B02
    # [흐름 이해]
    # 1) 슬라이싱(hits[:max_items]): 검색 후보가 여러 건 와도 앞에서 최대 max_items건(기본 2건)만 고릅니다.
    #    ※ hits가 빈 리스트([])여도 [][:2]는 에러 없이 빈 리스트([])를 돌려줍니다.
    # 2) 같은 for 반복문 안에서 '본문 블록(blocks)'과 '허용 출처 ID(included_ids)'를 동시에 모읍니다.
    #    → 이렇게 해야 모델이 실제로 읽은 Context와 검증용 included_ids가 100% 일치합니다!
    # 3) "\n\n".join(blocks): 여러 문서 블록이 섞이지 않도록 블록 사이에 빈 줄 하나(\n\n)를 넣어 합칩니다.
    #    ※ blocks가 비어 있으면 "\n\n".join([])은 자동으로 빈 문자열("")을 반환합니다.
    selected_hits = hits[:max_items]  # 실제 Context에 들어갈 후보만 먼저 확정

    blocks: list[str] = []            # format_hit()으로 꾸민 문자열 블록을 담을 목록
    included_ids: list[int] = []      # 위 blocks와 정확히 짝을 이루는 citation_id 목록

    for hit in selected_hits:
        blocks.append(format_hit(hit))       # 1) 출처가 붙은 본문 블록 추가
        included_ids.append(hit["citation_id"])  # 2) 같은 Hit의 정수 ID 추가

    context = "\n\n".join(blocks)     # 블록들을 빈 줄 하나로 연결해 최종 Context 문자열 완성

    # (최종 Context 문자열, 실제 포함된 ID 목록) 두 값을 튜플로 한 번에 반환합니다.
    return context, included_ids
    # END D26-02-B02


def main():
    # 1) 강의에서 제공한 고정 예시 데이터(출석 v2, ID=201) 1건을 가져옵니다.
    hit = example_hit()

    # 2) 리스트([hit]) 형태로 make_context에 넘겨 Context 문자열과 included_ids를 동시에 받습니다.
    context, included_ids = make_context([hit])

    # 3) 실행 결과를 JSON 리포트로 정리합니다.
    #    ※ 주의: character_count = len(context)는 단순 '글자 수'이며, LLM의 'Token 수'가 아닙니다!
    report = {
        "execution": execution_record("local_python"),
        "context": context,
        "included_ids": included_ids,
        "input_source": "lecture_fixture",
        "character_count": len(context),
    }

    # 4) outputs/hit_context.json 파일로 저장하고 성공 메시지를 출력합니다.
    path = save_json(HERE, "hit_context.json", report)
    show_success("02 기본필수", path)


if __name__ == "__main__":
    main()