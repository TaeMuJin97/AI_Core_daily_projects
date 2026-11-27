"""TEST 011: 출처 Validator 고정 Fixture 검증. 실행: python -m test.011_test."""


def main():
    from app.schemas.agent import ModelAnswer
    from app.services.validator import citation_ids
    allowed={'RPT-63':{}}
    good=ModelAnswer(status='completed',answer='예시 [RPT-63]',source_ids=['RPT-63'])
    bad=ModelAnswer(status='completed',answer='예시 [RPT-999]',source_ids=['RPT-999'])
    print(citation_ids(good,allowed),citation_ids(bad,allowed))
    assert citation_ids(good,allowed) is True
    assert citation_ids(bad,allowed) is False
    print("[PASS] TEST 011")


if __name__ == "__main__":
    main()
