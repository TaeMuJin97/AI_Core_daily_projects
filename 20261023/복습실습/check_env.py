"""환경 확인만 수행합니다. 설치나 컴퓨터 설정 변경은 하지 않습니다."""
import sys
from pathlib import Path

if __name__ == "__main__":
    print("Python:", sys.version.split()[0])
    print("실행기:", sys.executable)
    print("실습 폴더:", Path(__file__).resolve().parent)
    print("이번 자료는 Python 표준 라이브러리만 사용합니다. pip 설치가 필요하지 않습니다.")
    if sys.version_info < (3, 10):
        print("안내: 기존 수업의 Python 환경을 선택하세요. 검수 환경은 Python 3.13.5입니다.")
        raise SystemExit(1)
