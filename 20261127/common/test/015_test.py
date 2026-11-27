"""TEST 015: 최종 HTTP API 검증. 실행: python -m test.015_test."""


def main():
    import argparse
    from test._support import check_openapi, client, check_ready_http, check_response, report_ids, check_completed
    p = argparse.ArgumentParser()
    p.add_argument('--imports-only', action='store_true')
    p.add_argument('--allow-paid-llm', action='store_true')
    args = p.parse_args()
    if args.imports_only and args.allow_paid_llm:
        p.error('서버 실행 전 점검에서는 유료 플래그를 사용하지 않습니다.')
    check_openapi()
    if not args.imports_only:
        with client() as c:
            assert c.get('/docs').status_code == 200
            check_ready_http(c)
            if args.allow_paid_llm:
                rid, _ = report_ids()
                data = check_response(c.post('/api/v1/agent/ask', json={'question': f'보고서 {rid}의 핵심 내용과 인덱싱 상태를 함께 설명해 줘.'}), 200)
                check_completed(data, {'rag_search', 'lookup_status'})
                assert {source['report_id'] for source in data['sources']} == {rid}
    print("[PASS] TEST 015")


if __name__ == "__main__":
    main()
