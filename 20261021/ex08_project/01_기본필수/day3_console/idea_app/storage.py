"""JSON 읽기·전체 검사·저장. 실패를 빈 목록 또는 성공으로 위장하지 않습니다."""
import json
from pathlib import Path
from idea_app.models import from_record, to_record, name_key
from idea_app.io_support import write_json_atomic
REJECT_DUPLICATES = False

def validate_records(records):
    # 제공 코드 VALIDATE: 최상위 List·각 레코드·중복 이름을 전체 검사하고 독립적인 레코드 목록을 반환하세요.
    if not isinstance(records, list):
        raise ValueError("최상위 데이터는 List여야 합니다")
    validated, seen = [], set()
    for index, record in enumerate(records, start=1):
        try:
            idea = from_record(record)
        except ValueError as error:
            raise ValueError(f"레코드 {index}: {error}") from error
        key = name_key(idea.name)
        if REJECT_DUPLICATES and key in seen:
            raise ValueError(f"레코드 {index}: 이름 중복: {idea.name}")
        seen.add(key)
        validated.append(to_record(idea))
    return validated

def load_records(path):
    # TODO LOAD: UTF-8 JSON을 읽으세요. 파일 없음만 []로 처리하고 손상은 ValueError로 전달한 뒤 전체 검사하세요.
    raise NotImplementedError("TODO LOAD")

def save_records(path, records):
    # TODO SAVE: 전체 검사를 먼저 수행하고 제공된 write_json_atomic(path, records)로 저장하세요. 실패를 숨기지 마세요.
    raise NotImplementedError("TODO SAVE")
