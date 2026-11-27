"""B-02: /health는 설정 및 CUDA/DB 준비 확인이며 유료 모델 호출이 아니다."""
from app.services.errors import ServiceError

def require_cuda():
    import torch
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise ServiceError('GPU_UNAVAILABLE')
    return 'cuda:0'

def preflight(settings, repo):
    # BEGIN B-02
    state = repo.preflight()
    gpu = require_cuda()
    if not state['eligible_vectors']:
        raise ServiceError('EMBEDDING_UNAVAILABLE','no_eligible_vectors')
    if not settings.llm_configured:
        raise ServiceError('LLM_UNAVAILABLE','not_configured')
    return {**state,'gpu':gpu,'embedding_model':settings.embedding_model,
            'reranker_model':settings.reranker_model,'llm':'configured','llm_live_verified':False}
    # END B-02
