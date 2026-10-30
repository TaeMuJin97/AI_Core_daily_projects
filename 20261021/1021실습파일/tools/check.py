"""표준 라이브러리 확인 도구. 각 단계의 복사본을 임시 폴더에서 독립 검사합니다.
제출할 소스·data·reports를 변경하지 않습니다. 초급 수강생이 구현할 과제가 아닙니다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def main():
    parser=argparse.ArgumentParser(description="Day3 단계별 공개 검사")
    parser.add_argument("--list",action="store_true")
    parser.add_argument("--all",action="store_true")
    parser.add_argument("--exercise",choices=[f"{n:02d}" for n in range(1,9)])
    parser.add_argument("--level",choices=["basic","applied","advanced"])
    parser.add_argument("--syntax-only",action="store_true")
    parser.add_argument("--report",type=Path,help="검수 결과 JSON을 저장할 경로(선택)")
    args=parser.parse_args()
    entries=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    if args.list or (not args.exercise and not args.all):
        for row in entries:
            print(f"{row['exercise']} {row['level']:8} | PPT {row['slide']:2}쪽 | {row['path']}")
        return 0
    chosen=[r for r in entries if (args.all or r['exercise']==args.exercise) and (args.level is None or r['level']==args.level)]
    if not chosen: parser.error("검사할 실습을 선택하세요")
    results=[]
    for row in chosen:
        src=ROOT/row['path']; label=f"실습 {row['exercise']} / {row['level']}"
        syntax_errors=[]; files=list(src.rglob("*.py"))
        for file in files:
            try: compile(file.read_text(encoding="utf-8"),str(file),"exec")
            except (SyntaxError,UnicodeError) as error: syntax_errors.append(str(error))
        if syntax_errors:
            result={"exercise":row['exercise'],"level":row['level'],"status":"SYNTAX_ERROR","tests":0,"detail":"\n".join(syntax_errors)}
        elif args.syntax_only:
            result={"exercise":row['exercise'],"level":row['level'],"status":"PASS","tests":0,"python_files":len(files),"detail":"문법 검사 통과; 실행 검사는 하지 않았습니다."}
        else:
            with tempfile.TemporaryDirectory(prefix="day3_check_") as temp:
                dest=Path(temp)/"실습 복사본"
                # data의 이전 결과를 가져오지 않아 첫 실행 테스트도 매번 동일합니다.
                ignore=shutil.ignore_patterns(".venv","__pycache__","*.pyc","outputs","expected_outputs","ideas.json","note.txt")
                shutil.copytree(src,dest,ignore=ignore)
                env=dict(os.environ,PYTHONIOENCODING="utf-8",PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
                try:
                    completed=subprocess.run([sys.executable,"-B","-X","utf8","checks.py"],cwd=dest,env=env,capture_output=True,text=True,encoding="utf-8",timeout=90)
                    detail=completed.stdout+completed.stderr
                    match=re.search(r"Ran (\d+) tests?",detail)
                    count=int(match.group(1)) if match else 0
                    status="PASS" if completed.returncode==0 and count>0 else ("TODO/FAIL" if "NotImplementedError" in detail else "FAIL")
                    result={"exercise":row['exercise'],"level":row['level'],"status":status,"tests":count,"detail":detail}
                except subprocess.TimeoutExpired:
                    result={"exercise":row['exercise'],"level":row['level'],"status":"TIMEOUT","tests":0,"detail":"90초 초과: 무한 반복·입력 대기 여부를 확인하세요."}
        results.append(result)
        print(f"[{result['status']}] {label}: {result['tests']} tests")
        if result['status']!='PASS': print(result['detail'][-7000:])
    total=sum(r['tests'] for r in results); success=sum(r['status']=='PASS' for r in results)
    print(f"\n{success}/{len(results)}개 단계 PASS · 실행한 테스트 {total}개")
    print("GitHub 커밋/PR·리뷰의 질·개인 기여는 자동 검사 대상이 아닙니다.")
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps({"python":sys.version,"steps":results,"tests_run":total,"passed_steps":success},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("검사 기록:",args.report)
    return 0 if success==len(results) else 1

if __name__=="__main__":
    raise SystemExit(main())
