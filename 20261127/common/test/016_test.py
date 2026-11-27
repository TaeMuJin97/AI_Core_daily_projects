"""TEST 016: 시작/종료 DB Snapshot 불변성 검증. 실행: python -m test.016_test."""


def main():
    import json
    from pathlib import Path
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    db=Database(load_settings())
    try:
        after=Repository(db).snapshot()
        before=json.loads(Path('outputs/db_before.json').read_text(encoding='utf-8'))
        Path('outputs/db_after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
        print('DB unchanged:', before==after)
        if before!=after:
            print('changed tables:', sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k)))
        assert before == after, 'DB 변경 감지: 임의 복구/재시드 금지'
    finally:
        db.close()
    print("[PASS] TEST 016")


if __name__ == "__main__":
    main()
