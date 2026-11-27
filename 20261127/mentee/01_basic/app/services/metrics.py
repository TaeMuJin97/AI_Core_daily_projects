"""B-14/A-07: 요청별 예산 및 실제 wall-clock/usage. 병렬 Tool 호출도 lock으로 제한."""
from threading import Lock
from time import perf_counter
from app.services.errors import ServiceError

class Meter:
    def __init__(self, settings):
        self.settings=settings
        self.lock=Lock()
        self.started=perf_counter()
        self.tool_calls=0
        self.model_calls=0
        self.stages=[]
        self.ledger={}
        self.fatal=None
        self.debug=[]
    def reserve(self, kind):
        with self.lock:
            name=kind+'_calls'
            maximum=getattr(self.settings,'max_'+name)
            if getattr(self,name)>=maximum:
                self.fatal=ServiceError('EXECUTION_LIMIT',kind+'_limit')
                raise self.fatal
            setattr(self,name,getattr(self,name)+1)
    def record(self, stage, start, usage=None):
        event={'stage':stage,'latency_ms':round((perf_counter()-start)*1000,3)}
        if usage is not None:
            event['usage']={k:v for k,v in usage.items() if k in ('input_tokens','output_tokens','total_tokens') and type(v) is int}
        with self.lock:
            self.stages.append(event)
    def save_tool(self, call_id, name, result, args):
        with self.lock:
            if not call_id or call_id in self.ledger:
                raise ServiceError('TOOL_CONTRACT_ERROR')
            self.ledger[call_id]={'name':name,'result':result,'args':args}
    def summary(self):
        usages=[s['usage'] for s in self.stages if 'usage' in s and 'total_tokens' in s['usage']]
        return {'measurement':'live_wall_clock','tool_calls':self.tool_calls,'model_calls':self.model_calls,
                'stages':self.stages,'total_tokens_reported':sum(x['total_tokens'] for x in usages) if usages else None,
                'usage_observed_calls':len(usages),'usage_missing_calls':max(0,self.model_calls-len(usages)),
                'latency_ms':round((perf_counter()-self.started)*1000,3)}
