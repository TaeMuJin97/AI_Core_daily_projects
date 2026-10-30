# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 00 | 심화
# 환경 진단과 격리 이유 설명 | PPT 13쪽
# 실행: python env_check.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

# [제공 코드] 진단용 표준 라이브러리이다. import와 예외처리는 다음 수업에서 다룬다.
import sys
from importlib.metadata import PackageNotFoundError, version

print(f"Python: {sys.version.split()[0]}")
print(f"실행기: {sys.executable}")
print(f"venv 사용: {sys.prefix != sys.base_prefix}")
for package in ("numpy", "pandas", "matplotlib"):
    try:
        installed = version(package)
    except PackageNotFoundError:
        installed = "미설치"
    print(f"{package}: {installed}")

# TODO 01: 전역 환경과 venv를 구분하는 이유를 본인의 말로 두 문장 작성하세요.
reason_1 = "TODO: 첫 번째 이유"
reason_2 = "TODO: 두 번째 이유"
print("격리 이유 1:", reason_1)
print("격리 이유 2:", reason_2)
