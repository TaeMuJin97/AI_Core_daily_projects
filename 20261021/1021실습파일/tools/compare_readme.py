"""오프라인 README 변경 비교. Git 커밋이나 GitHub PR을 생성하지 않습니다."""
import argparse
import difflib
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("before",type=Path); parser.add_argument("after",type=Path)
    args=parser.parse_args()
    try:
        first=args.before.read_text(encoding="utf-8").splitlines(keepends=True)
        second=args.after.read_text(encoding="utf-8").splitlines(keepends=True)
    except (OSError,UnicodeError) as error:
        parser.exit(1,f"파일 읽기 실패: {error}\n")
    diff="".join(difflib.unified_diff(first,second,fromfile=args.before.name,tofile=args.after.name))
    print(diff if diff else "내용 차이 없음",end="" if diff.endswith("\n") else "\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
