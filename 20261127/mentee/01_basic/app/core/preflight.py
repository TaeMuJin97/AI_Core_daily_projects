"""B-02: /health는 설정 및 CUDA/DB 준비 확인이며 유료 모델 호출이 아니다."""
from app.services.errors import ServiceError

def require_cuda():
    import torch
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise ServiceError('GPU_UNAVAILABLE')
    return 'cuda:0'

def preflight(settings, repo):
    # TODO B-02: repo.preflight()와 require_cuda()의 결과를 얻으세요. 유효 벡터 0 및 키/모델 미설정은 ServiceError. 상태 dict에 gpu, embedding_model, reranker_model, llm=configured 등을 담아 반환하세요.
    raise ServiceError('NOT_IMPLEMENTED','B-02')
    # END TODO B-02
