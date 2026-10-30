"""PPT와 동일한 기준 버전을 출력하는 제공 점검 도구. 설치·삭제를 수행하지 않습니다."""
import importlib.metadata
import sys
from pathlib import Path

def main():
    print("Python:",sys.version.split()[0])
    print("실행기:",sys.executable)
    print("가상환경:","사용 중" if sys.prefix!=sys.base_prefix else "현재 실행기는 venv가 아닙니다")
    print("PPT 기준: Python 3.13.x / NumPy 2.3.5 / pandas 2.2.3")
    missing=False
    for name,expected in (("numpy","2.3.5"),("pandas","2.2.3")):
        try: version=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            print(name,": 미설치 (requirements.txt를 확인하세요)"); missing=True
        else:
            print(name,version,"[기준 일치]" if version==expected else "[다른 버전: 강사와 먼저 확인]")
    print("실습 01~04·07과 프로젝트 기본필수는 NumPy/Pandas 없이 진행할 수 있습니다.")
    return 1 if missing else 0

if __name__=="__main__":
    raise SystemExit(main())
