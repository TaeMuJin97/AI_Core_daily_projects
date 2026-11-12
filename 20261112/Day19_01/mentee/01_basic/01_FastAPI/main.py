"""
==============================================================================
[실습 보고서: Day 19 오전 자율 실습 1 - 01_FastAPI/main.py 명세 기반 CRUD 구현]
1. 실험 목적: 오후에 진행할 PostgreSQL(ORM) 연동에 앞서, API 명세서(명세서.md)와
              예상 결과(예상결과.md)의 입출력 계약을 준수하는 FastAPI 서버를 완성함.
2. 핵심 포인트:
   - 정렬 및 은닉 (B-API-01): 내부 관리 값인 next_id는 숨기고, entries 목록을 id 오름차순으로 정렬하여 반환함.
   - 식별자 비교 (B-API-02): 리스트 인덱스가 아닌 실제 데이터의 고유 ID(entry["id"])를 기준으로 단건을 조회함.
   - 원자적 쓰기와 번호표 관리 (B-API-03 ~ 06): LOCK 블록 내부에서 생성(next_id 부여 및 +1),
     수정(위치 i 교체), 삭제(위치 i 제거, next_id 유지) 후 write_data(data)로 파일 영속성을 보장함.
==============================================================================
"""
from fastapi import FastAPI, HTTPException, Response
from storage import LOCK, read_data, write_data

from pydantic import BaseModel, Field


class KnowledgeWrite(BaseModel):
    # 세 필드는 모두 필수입니다. 길이 규칙은 공백 제거 규칙과 다릅니다.
    title: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=30)


class Knowledge(KnowledgeWrite):
    id: int


app = FastAPI(title="Day19 AM Knowledge API - Basic")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/knowledge", response_model=list[Knowledge])
def list_knowledge():
    with LOCK:
        data = read_data()
    # BEGIN B-API-01
    # TODO B-API-01: data의 entries를 id 오름차순으로 반환하세요. sorted(..., key=lambda e:
    # e["id"])를 사용할 수 있습니다. next_id는 응답하지 않습니다.
    # [핵심 구현 1: 내부용 next_id를 제외하고 entries 배열만 꺼내어 id 기준 오름차순 정렬 반환]
    return sorted(data["entries"], key=lambda e: e["id"])
    # END B-API-01


@app.get("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        # BEGIN B-API-02
        # TODO B-API-02: 반복 중인 entry의 id가 knowledge_id와 같을 때 entry를 반환하세요. 목록 인덱스와 ID를
        # 혼동하지 마세요.
        # [핵심 구현 2: 배열 인덱스가 아닌 항목의 고유 ID(entry["id"])가 요청 ID와 일치할 때 반환]
        if entry["id"] == knowledge_id:
            return entry
        # END B-API-02
    # 반복문을 끝까지 돌았는데도 일치하는 ID가 없으면 404 Not Found 예외 발생
    raise HTTPException(404, "Knowledge not found")


@app.post("/api/knowledge", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        # BEGIN B-API-03
        # TODO B-API-03: payload를 dict로 변환하여 entry에 넣고, data의 next_id 값을 entry의 id로
        # 넣으세요.
        # [핵심 구현 3: 검증된 요청 본문(payload)을 딕셔너리로 변환하고 새 고유 번호(next_id) 부여]
        entry = payload.model_dump()
        entry["id"] = data["next_id"]
        # END B-API-03

        # BEGIN B-API-04
        # TODO B-API-04: entry를 entries에 추가하고 next_id를 1 늘린 뒤 write_data(data)로 저장하세요.
        # [핵심 구현 4: 목록에 새 지식 추가, 다음 발급 번호 1 증가 후 JSON 파일에 영구 저장]
        data["entries"].append(entry)
        data["next_id"] += 1
        write_data(data)
        # END B-API-04
    return entry


@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id
                # BEGIN B-API-05
                # TODO B-API-05: 찾은 위치 i의 항목을 updated로 교체한 뒤 저장하세요. 같은 ID를 유지하고 다른 항목은 변경하지
                # 않습니다.
                # [핵심 구현 5: 기존 위치(i)의 데이터를 갱신된 딕셔너리(updated)로 교체하고 파일에 저장]
                data["entries"][i] = updated
                write_data(data)
                # END B-API-05
                return updated
    raise HTTPException(404, "Knowledge not found")


@app.delete("/api/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int, response: Response):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                # BEGIN B-API-06
                # TODO B-API-06: 찾은 위치 i의 항목 하나만 삭제하고 저장하세요. next_id는 줄이지 않습니다.
                # [핵심 구현 6: 찾은 인덱스(i)의 항목 1건만 제거(.pop)하고 파일에 저장 (next_id는 유지)]
                data["entries"].pop(i)
                write_data(data)
                # END B-API-06
                return Response(status_code=204)
    raise HTTPException(404, "Knowledge not found")