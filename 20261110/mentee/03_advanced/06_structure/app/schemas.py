"""
==============================================================================
[실습 보고서: app/schemas.py - Pydantic 입출력 데이터 계약(Schema) 정의]
- 역할: 클라이언트 요청 Body의 유효성 검증(KnowledgeWrite)과 서버 응답 구조(Knowledge)를 정의하며,
        Router에서 import하여 재사용할 수 있도록 독립 모듈로 분리함.
==============================================================================
"""
from pydantic import BaseModel, Field


# 입력 모델은 HTTP Body의 규칙입니다. DB 테이블이나 저장 코드가 아닙니다.
class KnowledgeWrite(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=30)


class Knowledge(KnowledgeWrite):
    id: int