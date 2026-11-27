"""B-12: FastAPI는 요청을 받고 서비스 결과를 반환한다."""
from uuid import uuid4
from fastapi import APIRouter,Request,Response
from app.schemas.agent import AskRequest,AskResponse
from app.services.metrics import Meter
from app.services.errors import ServiceError

router=APIRouter(prefix='/api/v1')
@router.post('/agent/ask',response_model=AskResponse)
def ask(body:AskRequest,request:Request,response:Response):
    runtime=request.app.state.get_runtime()
    runtime.health()
    request_id=str(uuid4());request.state.request_id=request_id;response.headers['X-Request-ID']=request_id;meter=Meter(runtime.settings)
    # BEGIN B-12
    try:
        out=runtime.agent.ask(request_id,body,meter)
    except ServiceError as exc:
        if hasattr(runtime,'runs'):
            runtime.runs.put(request_id,{'request_id':request_id,'status':'error','error_code':exc.code,'metrics':meter.summary()})
        raise
    if hasattr(runtime,'runs'):
        runtime.runs.put(request_id,{'request_id':request_id,'status':out['status'],'tool_trace':out['tool_trace'],
            'validation':out['validation'],'metrics':meter.summary()})
    return out
    # END B-12


@router.get('/agent/runs/{request_id}')
def get_run(request_id:str,request:Request):
    return request.app.state.get_runtime().runs.get(request_id)
