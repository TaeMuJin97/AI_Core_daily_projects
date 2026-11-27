"""B-04: Query Prefix와 정규화. GPU에 올라간 실제 모델을 재사용한다."""
from threading import Lock
from time import perf_counter
import math
from app.core.preflight import require_cuda
from app.services.errors import ServiceError

class E5:
    def __init__(self, settings):
        self.settings=settings
        self.model=None
        self.lock=Lock()
    def encode(self, query, meter):
        require_cuda()
        try:
            with self.lock:
                if self.model is None:
                    from sentence_transformers import SentenceTransformer
                    start=perf_counter()
                    self.model=SentenceTransformer(self.settings.embedding_model,device='cuda:0')
                    meter.record('embedding_model_load',start)
                if str(self.model.device) != 'cuda:0':
                    raise ServiceError('GPU_UNAVAILABLE')
                start=perf_counter()
                # BEGIN B-04
                vector=self.model.encode('query: '+query,normalize_embeddings=True,convert_to_numpy=True).tolist()
                # END B-04
                meter.record('query_embedding',start)
                if len(vector)!=384 or not all(math.isfinite(x) for x in vector) or abs(sum(x*x for x in vector)-1)>0.01:
                    raise ServiceError('EMBEDDING_UNAVAILABLE','invalid_vector')
                return vector
        except ServiceError:
            raise
        except Exception as exc:
            raise ServiceError('EMBEDDING_UNAVAILABLE','gpu_oom' if type(exc).__name__=='OutOfMemoryError' else 'model_error') from None
