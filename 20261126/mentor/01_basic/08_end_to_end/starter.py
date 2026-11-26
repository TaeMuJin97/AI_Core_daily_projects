"""미완성 TODO와 별개로 API를 열 수 있게 제공하는 고정 Starter. 수정 대상 아님."""
from coursekit.agent import run_agent

def make_api(api_response):
    from fastapi import FastAPI,HTTPException
    from pydantic import BaseModel,Field
    class Ask(BaseModel):
        question:str=Field(min_length=1,max_length=1000)
    app=FastAPI(title='Day29 Report Agent (Local Only)')
    @app.post('/api/agent/ask')
    def ask(body:Ask):
        try:return api_response(run_agent(body.question))
        except ValueError:raise HTTPException(422,'잘못된 입력')
        except PermissionError:raise HTTPException(403,'접근 정책 위반')
        except RuntimeError as exc:raise HTTPException(502,'Agent 결과/출처 검증 실패') from exc
        except Exception as exc:raise HTTPException(503,'Agent Tool 실행 실패') from exc
    return app
