"""
==============================================================================
[실습 보고서: app/repositories/json_knowledge.py - 데이터 저장소(Repository) 계층 분리]
1. 실험 목적: HTTP 통신 규칙(FastAPI/Router)과 무관하게 순수하게 JSON 파일(data/knowledge.json)을
              읽고 쓰는 데이터 접근 로직만을 전담하는 Repository 모듈을 구현함.
2. 핵심 포인트:
   - 경로 기준점 변경(parents[2]): 파일 위치가 app/repositories/ 아래로 깊어졌으므로, 프로젝트 루트의
     data 폴더를 가리키기 위해 Path(__file__).resolve().parents[2]를 사용함.
   - HTTP 독립성 유지: Repository 함수들은 HTTPException이나 Response 객체를 직접 다루지 않고,
     순수 파이썬 자료형(list, dict, None, bool)만 반환하여 향후 DB(PostgreSQL) 교체를 용이하게 함.
==============================================================================
"""
"""제공 코드: 파일 접근 보조 함수. 호출자가 같은 LOCK으로 읽기~저장을 묶습니다."""
import json
from pathlib import Path
from threading import Lock

# [경로 설정] 현재 파일(app/repositories/json_knowledge.py)에서 상위 2단계(parents[2])인 프로젝트 루트 기준 설정
BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data" / "knowledge.json"
LOCK = Lock()


def read_data() -> dict:
    # 파일이 없거나 JSON이 손상되면 예외를 알립니다. 빈 목록으로 덮어쓰지 않습니다.
    with DATA.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_data(data: dict) -> None:
    # 원본부터 비우지 않고 같은 폴더의 임시 파일을 완성한 다음 교체합니다.
    # 단일 프로세스의 같은 LOCK 아래에서만 호출합니다. DB 트랜잭션은 아닙니다.
    temp = DATA.with_suffix(".tmp")
    try:
        with temp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        temp.replace(DATA)
    finally:
            temp.unlink(missing_ok=True)


# [목록 조회 데이터 접근] 선택적 category 조건에 따라 필터링된 지식 리스트(list[dict]) 반환
def list_entries(category: str | None = None) -> list[dict]:
    with LOCK:
        data = read_data()
    entries = data["entries"]
    if category is not None:
        entries = [entry for entry in entries if entry["category"] == category]
    # BEGIN H06-02
    # TODO H06-02: Repository의 목록 조회 결과를 반환하세요. HTTP Response를 만들지 마세요.
    # [핵심 구현: HTTP 응답 객체가 아닌 순수 파이썬 리스트(entries)를 Router로 반환]
    return entries
    # END H06-02


# [상세 조회 데이터 접근] 일치하는 ID가 있으면 해당 dict를, 없으면 None을 반환 (404 판단은 Router에 위임)
def find_entry(knowledge_id: int) -> dict | None:
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        if entry["id"] == knowledge_id:
            return entry
    return None


# [생성 데이터 접근] 검증된 dict(fields)를 받아 next_id를 부여하고 파일에 저장한 뒤 생성된 dict 반환
def create(fields: dict) -> dict:
    with LOCK:
        data = read_data()
        entry = dict(fields)
        entry["id"] = data["next_id"]
        data["entries"].append(entry)
        data["next_id"] += 1
        write_data(data)
    return entry


# [수정 데이터 접근] 대상 ID를 찾아 교체 후 dict를 반환하며, 대상이 없으면 None 반환
def update(knowledge_id: int, fields: dict) -> dict | None:
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                updated = dict(fields)
                updated["id"] = knowledge_id
                data["entries"][i] = updated
                write_data(data)
                return updated
    return None


# [삭제 데이터 접근] 대상 ID를 찾아 삭제 성공 시 True, 대상이 없으면 False 반환
def delete(knowledge_id: int) -> bool:
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                data["entries"].pop(i)
                write_data(data)
                return True
    return False