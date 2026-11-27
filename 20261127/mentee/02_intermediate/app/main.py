from contextlib import asynccontextmanager
from threading import Lock
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.agent import router
from app.api.rag import router as rag_router
from app.services.errors import ServiceError

def create_app(runtime_factory=None):
    pass

app=create_app()

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000,access_log=False)
