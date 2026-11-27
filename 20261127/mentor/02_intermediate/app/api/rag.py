"""I-04: 검색 디버그 API. 검색과 Reranking의 실제 수치만 반환."""
from fastapi import APIRouter,Request
from app.schemas.agent import DebugRequest
from app.services.metrics import Meter
from app.services.errors import ServiceError
router=APIRouter(prefix='/api/v1')
@router.post('/rag/debug')
def debug(body:DebugRequest,request:Request):
    runtime=request.app.state.get_runtime();runtime.health()
    meter=Meter(runtime.settings)
    _,info=runtime.pipeline.retrieve(body.query,body.category_code,body.top_k,meter)
    return {**info,'metrics':meter.summary()}
