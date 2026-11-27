"""TEST 004: 실제 DB·GPU 준비와 두 보고서 ID 검증. 실행: python -m test.004_test."""


def main():
    import json
    from test._support import report_ids
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    from app.core.preflight import preflight
    s=load_settings(); db=Database(s)
    try:
        repo=Repository(db)
        state = preflight(s, repo)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        assert state['database'] == 'report_agent_lab' and state['gpu'] == 'cuda:0'
        assert state['eligible_vectors'] > 0 and state['llm_live_verified'] is False
        rid, missing = report_ids()
        found, absent = repo.lookup(rid), repo.lookup(missing)
        print(found); print(absent)
        assert found['status'] == 'found' and found['embedding_fresh'] is True
        assert absent['status'] == 'not_found'
    finally:
        db.close()
    print("[PASS] TEST 004")


if __name__ == "__main__":
    main()
