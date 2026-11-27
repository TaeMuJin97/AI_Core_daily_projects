"""API-03: 비식별 실행 요약, 최대 100개, 재시작하면 사라진다."""
from collections import OrderedDict
from threading import Lock
from copy import deepcopy
from app.services.errors import ServiceError
class RunStore:
    def __init__(self,limit=100):self.items=OrderedDict();self.lock=Lock();self.limit=limit
    def put(self,request_id,value):
        with self.lock:
            self.items[request_id]=deepcopy(value);self.items.move_to_end(request_id)
            while len(self.items)>self.limit:self.items.popitem(last=False)
    def get(self,request_id):
        with self.lock:
            if request_id not in self.items:raise ServiceError('RUN_NOT_FOUND')
            return deepcopy(self.items[request_id])
