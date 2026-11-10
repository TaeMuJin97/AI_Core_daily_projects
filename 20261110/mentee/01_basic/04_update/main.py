"""
==============================================================================
[실습 보고서: 04_update/main.py - PUT 기반 기존 지식 내용 수정 및 데이터 갱신]
1. 실험 목적: Path Parameter로 전달받은 지식 ID(knowledge_id)와 일치하는 기존 항목을 찾아
              클라이언트가 보낸 새 입력값(KnowledgeWrite)으로 교체하고 파일에 영구 저장함.
2. 핵심 포인트:
   - ID(식별자)와 Index(배열 위치)의 분리: entries 리스트의 위치(index i)와 고유 번호(id)는 다르므로
     enumerate를 통해 올바른 ID 위치를 탐색해야 함.
   - append() 금지와 안전한 교체: 새로운 항목을 덧붙이는 append() 대신 기존 인덱스 위치(data["entries"][i] = updated)에
     덮어씌워 ID와 전체 개수(length), next_id를 완벽히 유지함.
   - 404 및 422 방어: 끝까지 일치하는 ID를 못 찾으면 HTTPException(404)을 발생시키고,
     필수 필드가 누락되면 Pydantic 검증에 의해 422로 차단하여 기존 파일을 보호함.
3. 주요 산출물: PUT 실행 시 해당 ID의 title, content, category가 갱신되고 항목 수는 그대로 유지됨
==============================================================================
"""
"""같은 지식의 본문 수정. 실행: python -m uvicorn main:app --reload"""
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

# [수정 Route] PUT /api/knowledge/{knowledge_id} 요청 시 지정한 ID의 내용을 새 페이로드로 교체
@app.put("/api/knowledge/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    with LOCK:
        data = read_data()
        # enumerate를 사용해 현재 목록의 순서(인덱스 i)와 값(entry)을 동시에 추적
        for i, entry in enumerate(data["entries"]):
            # BEGIN B04-01
            # TODO B04-01: 현재 지식의 id와 요청 ID를 비교해 same_id에 넣으세요.
            # [핵심 구현 1: 현재 순회 중인 항목의 고유 ID와 Path로 전달된 수정 대상 ID 일치 여부(bool) 판정]
            same_id = (entry["id"] == knowledge_id)
            # END B04-01
            
            if same_id:
                updated = payload.model_dump()
                updated["id"] = knowledge_id  # 사용자가 임의로 바꿀 수 없도록 기존 ID를 유지해 고정
                
                # BEGIN B04-02
                # TODO B04-02: 찾은 위치 i의 지식 한 개를 updated로 교체하세요. append로 추가하지 마세요.
                # [핵심 구현 2: 덧붙이기(append)가 아니라 배열 내 해당 인덱스(i)의 요소를 교체]
                data["entries"][i] = updated
                # END B04-02
                
                # BEGIN B04-03
                # TODO B04-03: 교체한 data를 같은 LOCK 블록 안에서 파일에 저장하세요.
                # [핵심 구현 3: 갱신된 전체 데이터 딕셔너리를 파일에 기록하여 반영]
                write_data(data)
                # END B04-03
                
                return updated
                
    # 없는 ID를 새로 생성하지 않습니다. PUT에서도 세 입력 필드가 모두 필수입니다.
    # [중요] 일치하는 ID를 끝까지 찾지 못한 경우 404 예외 발생 (새로 생성하지 않음)
    raise HTTPException(404, "Knowledge not found")
