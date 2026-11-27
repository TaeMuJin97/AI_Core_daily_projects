"""B-12: FastAPI는 요청을 받고 서비스 결과를 반환한다."""
from uuid import uuid4
from fastapi import APIRouter,Request
from app.schemas.agent import AskRequest,AskResponse
from app.services.metrics import Meter
from app.services.errors import ServiceError

router=APIRouter(prefix='/api/v1')
@router.post('/agent/ask',response_model=AskResponse)
def ask(body:AskRequest,request:Request):
    runtime=request.app.state.get_runtime()
    runtime.health()
    request_id=str(uuid4());meter=Meter(runtime.settings)
    # BEGIN B-12
    return runtime.agent.ask(request_id,body,meter)
    # END B-12
