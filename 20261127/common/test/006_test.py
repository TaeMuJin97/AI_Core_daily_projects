"""TEST 006: DB Tool 직접 호출·중간 Runtime·HTTP 검증. 실행: python -m test.006_test."""


def direct_db():
    import json
    from test._support import report_ids
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.services.metrics import Meter
    from app.tools.db_tool import make_db_tool
    s=load_settings(); db=Database(s); m=Meter(s)
    try:
        rid, _ = report_ids()
        t=make_db_tool(Repository(db),f'보고서 {rid} 상태',m)
        schema = t.tool_call_schema.model_json_schema()
        print('model tool schema:', schema)
        assert 'report_id' in schema['properties'] and 'tool_call_id' not in schema['properties']
        msg=t.invoke({'name':'lookup_status','args':{'report_id':rid},'id':'direct-db-1','type':'tool_call'})
        print('message:',msg.type,msg.tool_call_id,json.loads(msg.content))
        assert msg.type == 'tool' and msg.tool_call_id == 'direct-db-1'
        assert msg.tool_call_id in m.ledger
        assert json.loads(msg.content)['status'] == 'found'
        assert json.loads(msg.content)['report_id'] == rid
        assert m.ledger[msg.tool_call_id]['result'] == json.loads(msg.content)
    finally:
        db.close()


def main():
    import argparse
    from test._support import client, check_ready_http, check_response, report_ids, check_completed
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--imports-only', action='store_true')
    mode.add_argument('--http', action='store_true')
    p.add_argument('--allow-paid-llm', action='store_true')
    args = p.parse_args()
    if args.allow_paid_llm and not args.http:
        p.error('--allow-paid-llm은 --http와 함께 사용하세요.')
    if args.imports_only:
        from app.agent import AgentService
        from app.core.runtime import Runtime
        print('Agent / Runtime imports OK')
    elif args.http:
        with client() as c:
            check_ready_http(c)
            if args.allow_paid_llm:
                rid, _ = report_ids()
                data = check_response(c.post('/api/v1/agent/ask', json={'question': f'보고서 {rid}의 현재 인덱싱 상태와 revision을 알려 줘.'}), 200)
                check_completed(data, {'lookup_status'})
    else:
        direct_db()
    print("[PASS] TEST 006")


if __name__ == "__main__":
    main()
