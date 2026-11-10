"""
==============================================================================
[실습 보고서: 03_advanced/06_structure/app/main.py - FastAPI 앱 조립(App Assembly)]
1. 실험 목적: 단일 파일(main.py)에 모여 있던 CRUD 로직과 파일 저장 코드를 분리하고,
              app/main.py에는 앱 인스턴스 생성과 Router 등록(include_router) 책임만 남김.
2. 핵심 포인트:
   - 관심사 분리(Separation of Concerns): main.py는 전체 부품을 조립하는 진입점 역할만 수행하며,
     HTTP 경로 처리(routers/knowledge.py)와 파일 I/O(repositories/json_knowledge.py)를 분리함.
   - APIRouter 결합: knowledge.router에 이미 prefix('/api/knowledge')가 선언되어 있으므로,
     include_router 호출 시 추가 prefix를 중복 지정하지 않고 그대로 연결함.
3. 실행 명령 주의: 폴더가 패키지(app/)로 구조화되었으므로 프로젝트 루트에서
   'python -m uvicorn app.main:app --host 127.0.0.1 --port 18080 --reload'로 실행해야 함.
==============================================================================
"""
"""HTTP와 저장 책임을 구분하는 지식 관리 API입니다."""
from fastapi import FastAPI
from app.routers import knowledge

# [앱 객체 생성] 전체 서비스의 진입점이 되는 FastAPI 인스턴스 생성
app = FastAPI(title="Knowledge API")

# BEGIN H06-01
# TODO H06-01: knowledge 모듈의 router를 app에 포함하세요. 추가 prefix를 붙이지 마세요.
# [핵심 구현: 분리된 app/routers/knowledge.py 모듈의 router 객체를 메인 앱에 조립]
# (knowledge.router 내부에 이미 prefix="/api/knowledge"가 설정되어 있으므로 추가 인자 없이 연결)
app.include_router(knowledge.router)
# END H06-01


@app.get("/health")
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    return {"status": "ok"}