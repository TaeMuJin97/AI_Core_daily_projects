"""
==============================================================================
[실습 보고서: 05_delete/main.py - DELETE 기반 특정 지식 삭제 및 204 No Content 응답]
1. 실험 목적: Path Parameter로 전달된 지식 ID(knowledge_id)와 일치하는 항목을 찾아
              리스트에서 안전하게 제거하고 파일에 저장한 뒤, 본문 없는 204 상태코드를 반환함.
2. 핵심 포인트:
   - 부분 삭제 원칙: knowledge.json 파일 전체나 다른 정상 항목들을 건드리지 않고,
     일치하는 ID의 인덱스(i)만 pop(i)으로 정밀 타격하여 제거함.
   - 204 응답의 규격 (No Content): 삭제가 성공하면 본문(JSON Body)을 담지 않고 비운 채로
     Response(status_code=204)를 반환해야 하므로, 클라이언트도 response.json()을 호출하면 안 됨.
   - 실패 시 데이터 보호: 존재하지 않는 ID(404)나 잘못된 요청일 경우 파일 접근이나 저장이 일어나지 않아
     기존 데이터가 완벽히 보존됨.
3. 주요 산출물: DELETE 실행 시 해당 ID 항목만 목록에서 사라지고 next_id와 나머지 항목은 보존됨
==============================================================================
"""
"""삭제와 실패 후 데이터 보존. 실행: python -m uvicorn main:app --reload"""
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
    return data["entries"]

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
        write_data(data)
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
                data["entries"][i] = updated
                write_data(data)
                return updated
    # 없는 ID를 새로 생성하지 않습니다. PUT에서도 세 입력 필드가 모두 필수입니다.
    raise HTTPException(404, "Knowledge not found")

# [삭제 Route] DELETE /api/knowledge/{knowledge_id} 요청 시 해당 ID 항목을 제거하고 204 응답 반환
@app.delete("/api/knowledge/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
        for i, entry in enumerate(data["entries"]):
            if entry["id"] == knowledge_id:
                # BEGIN B05-01
                # TODO B05-01: 찾은 위치 i의 지식 한 개만 entries에서 제거하세요. 파일 전체를 삭제하지 마세요.
                # [핵심 구현 1: 리스트 내 해당 인덱스(i)의 항목만 pop() 메서드로 안전하게 추출 및 제거]
                data["entries"].pop(i)
                # END B05-01
                
                # BEGIN B05-02
                # TODO B05-02: 제거한 결과를 파일에 저장하세요. 다른 항목과 next_id는 유지하세요.
                # [핵심 구현 2: 항목이 하나 줄어든 갱신된 데이터를 파일에 기록하여 반영]
                write_data(data)
                # END B05-02
                
                # [중요] 삭제 성공 시 JSON 본문 없이 빈 상태코드 204(No Content)를 명시적으로 반환
                return Response(status_code=204)
                
    # 일치하는 ID가 없으면 삭제하지 않고 404 예외 발생
    raise HTTPException(404, "Knowledge not found")