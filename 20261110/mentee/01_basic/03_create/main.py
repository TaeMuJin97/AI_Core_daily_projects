"""
==============================================================================
[실습 보고서: 03_create/main.py - Pydantic 입력 검증 기반 새 지식 등록(POST) 및 파일 저장]
1. 실험 목적: 클라이언트가 보낸 JSON Body를 Pydantic 스키마로 검증하고, 고유 ID(next_id)를 발급해
              data/knowledge.json 파일에 영구 저장한 뒤 201 Created 응답을 반환함.
2. 핵심 포인트:
   - Pydantic 입력/응답 계약 분리: 입력용(KnowledgeWrite)은 필수 필드와 글자 수를 검증(실패 시 422 차단)하고,
     응답용(Knowledge)은 서버가 발급한 'id' 필드를 포함하여 반환 구조를 보장함.
   - 안전한 ID 발급 정책(next_id): 목록 길이(len)로 ID를 만들면 중간 항목 삭제 시 번호 충돌이 발생하므로,
     별도의 카운터인 data["next_id"]를 사용 후 +1 증가시켜 파일에 함께 저장함.
   - 원자적 잠금 범위(with LOCK): '파일 읽기 -> ID 부여 및 목록 추가 -> 파일 쓰기' 전 과정을 하나의 LOCK 안에서 처리함.
3. 주요 산출물: POST 실행 시 data/knowledge.json에 새 항목(id=4)이 추가되고 next_id가 5로 갱신됨
==============================================================================
"""
"""안내문 등록과 파일 저장. 실행: python -m uvicorn main:app --reload"""
from fastapi import FastAPI, HTTPException, Response
from storage import LOCK, read_data, write_data

from pydantic import BaseModel, Field


# [중요] Pydantic 입력 스키마: POST/PUT 요청의 HTTP Body 형식과 길이 규칙을 검증 (위반 시 함수 실행 전 422 반환)
# 입력 모델은 HTTP Body의 규칙입니다. DB 테이블이나 저장 코드가 아닙니다.
class KnowledgeWrite(BaseModel):
    title: str = Field(min_length=1, max_length=80)       # 제목: 필수, 1~80자 (빈 문자열 "" 불가)
    content: str = Field(min_length=1, max_length=2000)   # 본문: 필수, 1~2000자
    category: str = Field(min_length=1, max_length=30)    # 분류: 필수, 1~30자


# [중요] Pydantic 응답 스키마: KnowledgeWrite의 3개 필드를 상속받고 서버가 부여한 정수형 id 필드를 추가
class Knowledge(KnowledgeWrite):
    id: int


# 앱 객체 생성 및 기본 조회 Route (실습 01~02와 동일)
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


# [생성 Route] POST /api/knowledge 요청 시 새 지식을 저장하고 201 상태코드와 생성된 항목(Knowledge 규격)을 반환
@app.post("/api/knowledge", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    # 하나의 잠금으로 현재 데이터 읽기 → ID 발급 → 저장을 함께 보호합니다.
    with LOCK:
        data = read_data()
        # 검증을 통과한 Pydantic 모델 객체(payload)를 파이썬 일반 딕셔너리(dict)로 변환
        entry = payload.model_dump()
        # 파일에 보관된 다음 발급 번호(초기값 4)를 새 항목의 고유 ID로 부여
        entry["id"] = data["next_id"]
        
        # BEGIN B03-01
        # TODO B03-01: 새 entry를 data 안의 entries 목록 끝에 한 번 추가하세요.
        # [핵심 구현 1: 새 지식 딕셔너리(entry)를 기존 entries 리스트 맨 뒤에 추가]
        data["entries"].append(entry)
        # END B03-01
        
        # BEGIN B03-02
        # TODO B03-02: 다음 생성에 쓸 next_id 값을 1 증가시키세요.
        # [핵심 구현 2: 다음 POST 요청에서 중복되지 않는 새 ID를 쓰도록 next_id를 1 증가 (예: 4 -> 5)]
        data["next_id"] += 1
        # END B03-02
        
        # BEGIN B03-03
        # TODO B03-03: 변경된 data 전체를 write_data에 전달해 저장하세요. LOCK 블록 안에서 호출하세요.
        # [핵심 구현 3: entries와 next_id가 갱신된 data 딕셔너리 전체를 JSON 파일에 물리적으로 기록]
        write_data(data)
        # END B03-03
        
    # 201을 선언하는 것만으로 저장되지는 않습니다. 실제 저장 성공 뒤 응답합니다.
    return entry