"""
==============================================================================
[실습 보고서: app/routers/knowledge.py - APIRouter 기반 HTTP 계약 및 라우팅 분리]
1. 실험 목적: '/api/knowledge' 공통 경로(prefix)를 가지는 CRUD 엔드포인트들을 APIRouter로 묶고,
              실제 파일 읽기/쓰기는 Repository(json_knowledge)에 위임함.
2. 핵심 포인트:
   - prefix와 Path 결합: APIRouter에 prefix="/api/knowledge"를 지정했으므로, 개별 데코레이터에는
     빈 문자열("")이나 "/{knowledge_id}"만 적어 경로 중복을 방지함.
   - HTTP 상태코드 및 예외 변환: Repository가 None이나 False를 반환하면 Router가 이를 해석해
     HTTPException(404)을 발생시키고, 삭제 성공(True) 시 빈 204 Response를 생성함.
==============================================================================
"""
"""HTTP 경로·입력·응답. 저장 구현은 repository에 위임합니다."""
from fastapi import APIRouter, HTTPException, Response
from app.schemas import Knowledge, KnowledgeWrite
from app.repositories import json_knowledge as repo

# [라우터 생성] 공통 URL 접두사(/api/knowledge)와 Swagger UI(/docs) 그룹 태그(knowledge) 설정
router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("", response_model=list[Knowledge])
def list_knowledge(category: str | None = None):
    return repo.list_entries(category)


@router.get("/{knowledge_id}", response_model=Knowledge)
def get_knowledge(knowledge_id: int):
    entry = repo.find_entry(knowledge_id)
    if entry is None:
        raise HTTPException(404, "Knowledge not found")
    return entry


@router.post("", status_code=201, response_model=Knowledge)
def create_knowledge(payload: KnowledgeWrite):
    # BEGIN H06-03
    # TODO H06-03: 검증된 payload를 dict로 바꾸어 repo.create에 전달하고 결과를 반환하세요.
    # [핵심 구현: Pydantic 모델(payload)을 model_dump()로 dict 변환 후 Repository의 create 함수 호출]
    return repo.create(payload.model_dump())
    # END H06-03


@router.put("/{knowledge_id}", response_model=Knowledge)
def update_knowledge(knowledge_id: int, payload: KnowledgeWrite):
    updated = repo.update(knowledge_id, payload.model_dump())
    if updated is None:
        raise HTTPException(404, "Knowledge not found")
    return updated


@router.delete("/{knowledge_id}", status_code=204)
def delete_knowledge(knowledge_id: int):
    deleted = repo.delete(knowledge_id)
    if not deleted:
        raise HTTPException(404, "Knowledge not found")
    return Response(status_code=204)