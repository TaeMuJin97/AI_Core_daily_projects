"""TEST 005: 최초 DB Snapshot 저장. 실행: python -m test.005_test."""


def main():
    import argparse
    import json
    from pathlib import Path
    from app.core.settings import load_settings
    from app.db.connection import Database
    from app.db.repository import Repository
    p = argparse.ArgumentParser()
    p.add_argument('--replace-baseline', action='store_true', help='새 점검을 시작할 때만 기존 기준 교체')
    args = p.parse_args()
    out = Path('outputs/db_before.json')
    # 실수로 기존 검증의 기준선을 덮어쓰지 않는다.
    if out.exists() and not args.replace_baseline:
        raise SystemExit('기존 db_before.json이 있습니다. 기존 기준을 보존하세요. 새 점검에 한해 --replace-baseline 사용.')
    db = Database(load_settings())
    try:
        snap = Repository(db).snapshot()
        assert len(snap) == 10
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding='utf-8')
        print('snapshot tables:', len(snap))
    finally:
        db.close()
    print("[PASS] TEST 005")


if __name__ == "__main__":
    main()
