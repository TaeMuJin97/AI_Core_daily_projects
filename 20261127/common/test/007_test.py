"""TEST 007: E5 실제 CUDA 384차원 벡터 검증. 실행: python -m test.007_test."""


def main():
    import math
    from app.core.settings import load_settings
    from app.services.metrics import Meter
    from app.rag.embeddings import E5
    s=load_settings(); meter=Meter(s); e=E5(s)
    v=e.encode('RAG 근거 인용 정확도 향상',meter)
    print('device:',e.model.device,'dimension:',len(v))
    print('finite:',all(math.isfinite(x) for x in v),'norm_squared:',sum(x*x for x in v))
    print('first 5:',v[:5]); print(meter.summary())
    assert str(e.model.device) == 'cuda:0' and len(v) == 384
    assert all(math.isfinite(x) for x in v) and abs(sum(x*x for x in v)-1) <= 0.01
    print("[PASS] TEST 007")


if __name__ == "__main__":
    main()
