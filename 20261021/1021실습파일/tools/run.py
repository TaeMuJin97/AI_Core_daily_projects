"""제공 실행 런처. 같은 Python으로 대상 단계를 실행하며 소스 경로를 수정하지 않습니다."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser(description="Day3 실습 실행",allow_abbrev=False)
    parser.add_argument("--exercise",required=True,choices=[f"{n:02d}" for n in range(1,9)])
    parser.add_argument("--level",default="basic",choices=["basic","applied","advanced"])
    parser.add_argument("--sample",action="store_true",help="sample_input.txt 내용을 stdin으로 공급")
    args,forward=parser.parse_known_args()
    entries=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    row=next(r for r in entries if r['exercise']==args.exercise and r['level']==args.level)
    base=ROOT/row['path']; target=base/row['entry']
    command=[sys.executable,"-X","utf8",str(target),*forward]
    if args.sample:
        text=(base/"sample_input.txt").read_text(encoding="utf-8")
        result=subprocess.run(command,cwd=target.parent,input=text,text=True,encoding="utf-8")
    else:
        result=subprocess.run(command,cwd=target.parent)
    return result.returncode

if __name__=="__main__":
    raise SystemExit(main())
