"""
==============================================================================
[실습 보고서: 02_read/main.py - JSON 원본 지식 목록 조회 및 ID 기반 상세 조회]
1. 실험 목적: data/knowledge.json 파일을 읽어 전체 지식 목록(GET /api/knowledge)과
              특정 ID의 상세 지식(GET /api/knowledge/{knowledge_id})을 반환하는 Read API를 구현함.
2. 핵심 포인트:
   - 내부 상태 은닉: JSON 파일에는 내부 발급용 'next_id'가 포함되어 있으나, 클라이언트에는
     순수 지식 목록인 'entries' 배열만 노출하여 데이터 계약을 분리함.
   - Path Parameter와 자동 타입 검증: 함수 인자에 'knowledge_id: int' 타입을 명시하면,
     숫자가 아닌 값(예: /api/knowledge/foo) 요청 시 함수 실행 전에 FastAPI가 422 오류로 자동 차단함.
   - return vs raise: 대상을 찾으면 return으로 200 응답을 주고, 끝까지 없으면 raise HTTPException(404)으로 예외를 발생시킴.
3. 주요 산출물: 조회(GET) 전용 실습이므로 data/knowledge.json 원본 파일은 변경되지 않음 (불변 유지)
==============================================================================
"""
"""JSON 목록·상세 조회. 실행: python -m uvicorn main:app --reload"""
from fastapi import FastAPI, HTTPException, Response
from storage import LOCK, read_data, write_data

# FastAPI 앱 인스턴스 생성 및 기본 /health 체크 (실습 01과 동일)
app = FastAPI(title="Knowledge API", description="AI 플랫폼의 원본 지식 관리 연습")


@app.get("/health")
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    return {"status": "ok"}


# [목록 조회 Route] GET /api/knowledge 요청 시 저장된 전체 지식 항목 리스트를 반환
@app.get("/api/knowledge")
def list_knowledge():
    # 동시 접근 시 파일 읽기 충돌을 방지하기 위해 LOCK 안에서 JSON 데이터를 읽어옴
    with LOCK:
        data = read_data()
    # 파일 전체에는 내부용 next_id도 있으므로 entries만 응답합니다.
    # BEGIN B02-01
    # TODO B02-01: 파일 전체 data에서 entries 목록만 반환하세요. next_id가 포함된 dict 전체를 반환하지 마세요.
    # [핵심 구현: 전체 딕셔너리(data) 중 지식 목록 배열인 'entries'만 추출하여 반환 (JSON 배열로 직렬화됨)]
    return data["entries"]
    # END B02-01


# [상세 조회 Route] URL 경로의 {knowledge_id} 값을 정수(int)로 받아 일치하는 지식 1건을 반환
@app.get("/api/knowledge/{knowledge_id}")
def get_knowledge(knowledge_id: int):
    with LOCK:
        data = read_data()
    
    # 저장된 지식 목록(entries)을 하나씩 순회하며 요청받은 ID와 일치하는 항목 탐색
    for entry in data["entries"]:
        # BEGIN B02-02
        # TODO B02-02: 현재 entry의 id와 요청 knowledge_id가 같은지 비교하여 same_id에 저장하세요.
        # 힌트: 비교 결과는 True 또는 False입니다.
        # [핵심 구현: 현재 항목의 고유 식별자(entry["id"])와 Path로 전달된 knowledge_id의 일치 여부(bool) 판정]
        same_id = (entry["id"] == knowledge_id)
        # END B02-02
        if same_id:
            return entry  # 일치하는 항목을 찾으면 즉시 해당 dict를 반환 (200 OK)
            
    # 입력은 정수이지만 저장된 항목이 없으면 404입니다. foo 같은 Path는 먼저 422입니다.
    # [중요] 오류 응답은 return이 아니라 raise로 HTTPException을 던져야 정상적인 404 상태코드가 전달됨
    raise HTTPException(404, "Knowledge not found")
