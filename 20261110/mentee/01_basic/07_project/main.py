"""
==============================================================================
[실습 보고서: 01_basic/07_project/main.py - Day 17 종합 CRUD 프로젝트 완성]
1. 실험 목적: 지금까지 개별로 실습했던 조회(GET), 생성(POST), 수정(PUT), 삭제(DELETE)
              모든 기능을 하나의 단일 모듈에 통합하고, JSON 파일 영구 저장 및 예외 처리를 검증함.
2. 핵심 포인트:
   - 통합 CRUD 구조: Pydantic 스키마 검증, LOCK을 이용한 동시성 제어, 임시 파일을 이용한 안전한 원자적 쓰기(write_data)를 모두 결합함.
   - 규격 준수 응답: 목록은 entries 배열 반환, 생성은 201과 id 부여, 삭제는 본문 없는 204 No Content를 반환함.
==============================================================================
"""
"""함께 통합하고 프로젝트 준비. 실행: python -m uvicorn main:app --reload"""
from fastapi import FastAPI, HTTPException, Response
from storage import LOCK, read_data, write_data

from pydantic import BaseModel, Field

# 입력 모델은 HTTP Body의 규칙입니다. DB 테이블이나 저장 코드가 아닙니다.
class KnowledgeWrite(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=30)


class Knowledge(KnowledgeWrite):
    id: int


app = FastAPI(title="Knowledge API", description="AI 플랫폼의 원본 지식 관리 연습")

@app.get("/health")
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    return {"status": "ok"}

@app.get("/api/knowledge")
def list_knowledge():
    with LOCK:
        data = read_data()
    # 파일 전체에는 내부용 next_id도 있으므로 entries만 응답합니다.
    # BEGIN B07-01
    # TODO B07-01: 통합 목록 Route에서 entries만 응답하도록 연결하세요.
    # [핵심 구현: 전체 딕셔너리 중 지식 목록 배열인 'entries'만 추출하여 반환]
    return data["entries"]
    # END B07-01

@app.get("/api/knowledge/{knowledge_id}")
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    for entry in data["entries"]:
        same_id = entry["id"] == knowledge_id
        if same_id:
            return entry
    # 입력은 정수이지만 저장된 항목이 없으면 404입니다. foo 같은 Path는 먼저 422입니다.
    raise HTTPException(404, "Knowledge not found")

@app.post("/api/knowledge", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    # 하나의 잠금으로 현재 데이터 읽기 → ID 발급 → 저장을 함께 보호합니다.
    with LOCK:
        data = read_data()
        entry = payload.model_dump()
        entry["id"] = data["next_id"]
        data["entries"].append(entry)
        data["next_id"] += 1
        # BEGIN B07-02
        # TODO B07-02: 생성된 지식과 증가한 next_id를 파일에 함께 저장하세요.
        # [핵심 구현: entries와 next_id가 갱신된 data 전체를 파일에 영구 기록]
        write_data(data)
        # END B07-02
    # 201을 선언하는 것만으로 저장되지는 않습니다. 실제 저장 성공 뒤 응답합니다.
    return entry

@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            same_id = entry["id"] == knowledge_id
            if same_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id
                # BEGIN B07-03
                # TODO B07-03: 같은 ID의 위치 i를 updated로 교체하세요.
                # [핵심 구현: append가 아닌 해당 인덱스(i) 위치에 갱신된 데이터를 덮어씌움]
                data["entries"][i] = updated
                # END B07-03
                write_data(data)
                return updated
    # 없는 ID를 새로 생성하지 않습니다. PUT에서도 세 입력 필드가 모두 필수입니다.
    raise HTTPException(404, "Knowledge not found")

@app.delete("/api/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                data["entries"].pop(i)
                write_data(data)
                # BEGIN B07-04
                # TODO B07-04: 삭제 저장 후 본문 없는 204 응답을 반환하세요. dict 또는 JSON 문자열을 넣지 마세요.
                # [핵심 구현: 삭제 성공 시 본문 없이 비어 있는 204 No Content 응답 객체 반환]
                return Response(status_code=204)
                # END B07-04
    raise HTTPException(404, "Knowledge not found")