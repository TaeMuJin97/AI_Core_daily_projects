# 검증용 Reference tests
실제 실행과 구분되는 Fixture/Stub 테스트입니다. 필요 시 선택한 난이도의 tests/로 복사합니다. Mentor 구현의 함수 경로와 계약을 기준으로 작성했으므로 수강생이 구조를 다르게 설계했다면 import/adapter를 맞추고 명세의 검증 기준은 변경하지 않습니다. LangChain이 설치되어야 framework 실제 실행 테스트가 수행됩니다. skip은 pass가 아닙니다.

프로젝트 루트에서 `python -m pytest tests/ -q -ra`를 실행합니다. 별도로 공통 참조 테스트를 확인하려면 선택한 난이도 폴더 **하나만** 지정하세요. 동일 이름의 테스트 모듈과 상위 난이도의 미구현 import 때문에 `common/tests` 전체를 동시에 수집하면 오류가 발생할 수 있습니다. 프로젝트 루트의 `pytest.ini`는 `testpaths = tests`로 유지합니다.
