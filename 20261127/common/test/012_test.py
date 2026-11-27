"""TEST 012: 최종 Runtime 조립 검증. 실행: python -m test.012_test."""


def main():
    from app.core.runtime import Runtime
    from app.rag.pipeline import RagPipeline
    r = Runtime()
    try:
        assert isinstance(r.pipeline, RagPipeline)
        assert r.agent.pipeline is r.pipeline
        print('Runtime / Agent / RagPipeline connected')
    finally:
        r.close()
    print("[PASS] TEST 012")


if __name__ == "__main__":
    main()
