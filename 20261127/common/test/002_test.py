"""TEST 002: 최초 API 뼈대와 미구현 차단 검증. 실행: python -m test.002_test."""


def main():
    import argparse
    from test._support import check_openapi, client, check_response
    p = argparse.ArgumentParser()
    p.add_argument('--imports-only', action='store_true', help='서버 실행 전 OpenAPI 확인')
    args = p.parse_args()
    check_openapi()
    if not args.imports_only:
        # 실제 실행 중인 초기 FastAPI 서버를 확인한다. 유료 호출 없음.
        with client() as c:
            assert c.get('/docs').status_code == 200
            paths = c.get('/openapi.json').raise_for_status().json()['paths']
            assert {'/health', '/api/v1/agent/ask'} <= set(paths)
            data = check_response(c.get('/health'), 500, 'NOT_IMPLEMENTED')
            assert data['error']['details']['reason'] == 'runtime_pending'
            check_response(c.post('/api/v1/agent/ask', json={'question': ' '}), 422, 'VALIDATION_ERROR')
            # 정상 형식 질문도 초기 Runtime이면 미구현으로 차단된다.
            # 이미 완성한 서버에 이 단계의 요청을 보내지 않는다.
            data = check_response(c.post('/api/v1/agent/ask', json={'question': '보고서 63의 상태를 알려 줘.'}), 500, 'NOT_IMPLEMENTED')
            assert data['error']['details']['reason'] == 'runtime_pending'
    print("[PASS] TEST 002")


if __name__ == "__main__":
    main()
