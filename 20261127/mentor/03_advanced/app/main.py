"""B-01/B-12: python -m app.main 또는 uvicorn app.main:app."""
from contextlib import asynccontextmanager
from threading import Lock
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.agent import router
from app.api.rag import router as rag_router
from app.services.errors import ServiceError

def create_app(runtime_factory=None):
    # Lazy DI: import/Swagger/422 검증에 DB·GPU·키가 없어도 된다.
    if runtime_factory is None:
        def runtime_factory():
            from app.core.runtime import Runtime
            return Runtime()
    holder={};lock=Lock()
    def get_runtime():
        with lock:
            if 'runtime' not in holder:
                holder['runtime']=runtime_factory()
            return holder['runtime']
    @asynccontextmanager
    async def lifespan(app):
        yield
        if 'runtime' in holder:
            holder.pop('runtime').close()
    app=FastAPI(title='Day30 Technical Report Agent',version='1.0',lifespan=lifespan)
    app.state.get_runtime=get_runtime
    @app.exception_handler(ServiceError)
    async def known(request,exc):
        return JSONResponse(status_code=exc.http_status,content=exc.envelope(),headers={'X-Request-ID':request.state.request_id} if hasattr(request.state,'request_id') else None)
    @app.exception_handler(RequestValidationError)
    async def invalid(request,exc):
        return JSONResponse(status_code=422,content=ServiceError('VALIDATION_ERROR').envelope())
    @app.exception_handler(NotImplementedError)
    async def todo(request,exc):
        return JSONResponse(status_code=500,content=ServiceError('NOT_IMPLEMENTED').envelope())
    @app.exception_handler(Exception)
    async def unknown(request,exc):
        return JSONResponse(status_code=500,content=ServiceError('TOOL_CONTRACT_ERROR','internal_error').envelope())
    @app.get('/health')
    def health():
        return get_runtime().health()
    app.include_router(router)
    app.include_router(rag_router)
    return app
app=create_app()
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000,access_log=False)
