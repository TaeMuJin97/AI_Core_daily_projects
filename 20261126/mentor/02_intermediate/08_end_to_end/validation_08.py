"""용도별 추가 검증: Intermediate · Day29."""

def make_api():
    """FastAPI에 POST /api/agent/ask 를 등록합니다. 로컬 교육용·인증 미구현."""
    # 해설 D29-08-I-03: FastAPI는 사용자의 입력을 검증해 Agent에 전달하고 최종 결과를 반환합니다.
    # 검수 기준: 인용 ID가 실제 Tool 근거 집합 밖이면 성공 응답으로 위장하지 않습니다.
    from fastapi import FastAPI,HTTPException
    from pydantic import BaseModel,Field
    from coursekit.agent import run_agent
    class Ask(BaseModel):
        question:str=Field(min_length=1,max_length=1000)
    app=FastAPI(title='Day29 Existing Report DB Agent',version='1.0')
    @app.post('/api/agent/ask')
    def ask(body:Ask):
        try:return api_response(run_agent(body.question))
        except (ValueError,PermissionError) as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc
        except Exception as exc:raise HTTPException(status_code=503,detail='Agent/DB/GPU/LLM 실행 실패') from exc
    return app

