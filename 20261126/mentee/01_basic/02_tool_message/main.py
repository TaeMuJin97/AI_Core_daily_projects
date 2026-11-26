"""02 · AIMessage.tool_calls / ToolMessage · 기본필수 · 실제 11/20 report_agent_lab 기반 실습."""
from pathlib import Path
import sys,argparse
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import tasks


def main():
    ap=argparse.ArgumentParser(description='Day29 · 기존 DB 재사용 / CPU fallback 없음')
    ap.add_argument('--check',action='store_true',help='실제 DB/API 없이 순수 함수 TODO 자가 점검 (실제 실습 아님)')
    ap.add_argument('--serve',action='store_true',help='실습 08 FastAPI 실행(실제 DB·GPU·LLM)')
    args=ap.parse_args()
    if args.check:
        # 실습 진입점에서의 확인은 코드 구조만 진단합니다. 정답 코드는 학생이 작성합니다.
        print('TODO 함수:',[name for name in dir(tasks) if not name.startswith('_') and callable(getattr(tasks,name))])
        print('실제 연동은 --check 없이 실행해야 합니다.')
        return
    serve=args.serve
    from coursekit.db import fetch_report_status
    raw=fetch_report_status(63)
    call=tasks.make_request('lookup_status',{'report_id':63},'call_001')
    print('[실제 DB 조회]',raw)
    print('[ToolMessage]',tasks.match_result(call,raw))

if __name__=='__main__':main()
