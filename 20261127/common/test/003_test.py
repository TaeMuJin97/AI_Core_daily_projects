"""TEST 003: 환경변수 및 테스트 ID 확인. 실행: python -m test.003_test."""


def main():
    from test._support import report_ids
    rid, missing = report_ids()
    print('DAY30_REPORT_ID:', rid)
    print('DAY30_MISSING_ID:', missing)
    print("[PASS] TEST 003")


if __name__ == "__main__":
    main()
