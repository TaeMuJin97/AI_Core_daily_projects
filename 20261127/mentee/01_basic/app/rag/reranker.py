"""B-07: 동일 후보의 순위만 CUDA Cross-Encoder로 변경한다."""
import math
from threading import Lock
from time import perf_counter
from app.core.preflight import require_cuda
from app.services.errors import ServiceError

class Reranker:
    def __init__(self,settings):
        self.settings=settings;self.model=None;self.lock=Lock()
    def rank(self,query,docs,meter):
        if not docs:
            return []
        require_cuda()
        try:
            with self.lock:
                if self.model is None:
                    from sentence_transformers import CrossEncoder
                    start=perf_counter()
                    self.model=CrossEncoder(self.settings.reranker_model,device='cuda:0',max_length=self.settings.rerank_max_length)
                    meter.record('reranker_model_load',start)
                if str(self.model.model.device)!='cuda:0':
                    raise ServiceError('GPU_UNAVAILABLE')
                start=perf_counter()
                # TODO B-07: (query, title + overview) 쌍 목록을 만들고 self.model.predict(..., batch_size=..., show_progress_bar=False)를 호출하세요. docs와 scores를 zip하여 점수 내림차순, ID 오름차순으로 ranked를 구성하세요.
                raise ServiceError('NOT_IMPLEMENTED','B-07')
                # END TODO B-07
                meter.record('cross_encoder_rerank',start)
                if len(ranked)!=len(docs) or any(not math.isfinite(float(s)) for _,s in ranked):
                    raise ServiceError('RERANKER_UNAVAILABLE','invalid_score')
                return [d.model_copy(update={'metadata':{**d.metadata,'reranker_score':float(s)}}) for d,s in ranked]
        except ServiceError:
            raise
        except Exception as exc:
            raise ServiceError('RERANKER_UNAVAILABLE','gpu_oom' if type(exc).__name__=='OutOfMemoryError' else 'model_error') from None
