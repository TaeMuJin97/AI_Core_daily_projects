"""
==============================================================================
[실습 보고서: 01_first_server/main.py - FastAPI 첫 서버 구동 및 Health Check 응답]
1. 실험 목적: FastAPI 앱 객체를 생성하고 GET /health 경로를 등록하여, Uvicorn 서버를 통해
              첫 HTTP 200 응답과 JSON 직렬화 결과를 확인함.
2. 핵심 포인트:
   - 데코레이터 라우팅(@app.get): 특정 URL 경로('/health')와 HTTP Method(GET)를 파이썬 처리 함수와 연결함.
   - 자동 JSON 직렬화: 파이썬 함수가 dict({"status": "ok"})를 반환(return)하면, FastAPI가 이를
     HTTP 응답 본문(Content-Type: application/json)으로 자동 변환하여 클라이언트에 전달함.
   - print() vs return: print()는 서버 터미널에만 찍히는 로그일 뿐 클라이언트에게 전달되지 않으므로,
     반드시 return 문을 통해 응답 데이터를 반환해야 함.
3. 주요 산출물: 별도 생성 파일 없음 (main.py 소스 코드만 Git 업로드 대상)
==============================================================================
"""
"""내 PC에서 첫 요청 성공시키기. 실행: python -m uvicorn main:app --reload"""
from fastapi import FastAPI, HTTPException, Response

# [앱 객체 생성] Uvicorn이 실행할 FastAPI 인스턴스(app)를 생성하고 문서(/docs)에 표시될 제목과 설명을 지정
app = FastAPI(title="Knowledge API", description="AI 플랫폼의 원본 지식 관리 연습")


# [경로 등록] 클라이언트가 GET 방식으로 '/health' 주소에 요청을 보낼 때 아래 함수를 실행하도록 연결
@app.get("/health")
def health():
    # 이 경로의 응답 확인입니다. 파일·DB·AI 모델의 전체 상태 점검은 아닙니다.
    # BEGIN B01-01
    # 해설 B01-01: dict를 return하면 FastAPI가 JSON 응답으로 직렬화합니다.
    # 해설 B01-01: print는 서버 터미널 출력이므로 HTTP 응답을 대신하지 않습니다.
    # [핵심 구현: 상태코드 200 OK와 함께 JSON으로 변환될 파이썬 딕셔너리 반환]
    return {"status": "ok"}
    # END B01-01


#   bash 창에서 아래 명령어를 통해 서버를 실행할 수 있습니다.
#   python -m uvicorn main:app --host 127.0.0.1 --port 18080 --reload