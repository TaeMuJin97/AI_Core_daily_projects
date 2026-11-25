"""Day28 실습 04 · 01_basic · 실행 진입점.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""
from pathlib import Path
import argparse
import sys

ROLE_ROOT = Path(__file__).resolve().parents[2]
if str(ROLE_ROOT) not in sys.path:
    sys.path.insert(0,str(ROLE_ROOT))

from coursekit.eval_workshops import execute
from coursekit.eval_report import write_json


def first_relevant_rank(ranked: list[str], gold: list[str], k: int) -> int | None:
    """Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None."""
    # 정답 D28-04-B01: Top-k에서 첫 Gold 문서가 등장하는 1부터 시작하는 순위를 찾으세요. 없으면 None.
    # 절차: enumerate(..., start=1)을 활용하세요.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    for pos,cid in enumerate(ranked[:k],1):
        if cid in gold:
            return pos
    return None

def calculate_rr(position: int | None) -> float:
    """관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다."""
    # 정답 D28-04-B02: 관련 문서 첫 순위의 역수(1/rank)를 반환하세요. 문서가 없으면 0.0입니다.
    # 절차: Gold가 아예 없는 No-answer 사례는 집계 대상에서 제외합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    return 1.0/position if position is not None else 0.0


def main():
    parser=argparse.ArgumentParser(description="Day28 RAG Evaluation 실습")
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--offline',action='store_true',help='고정 학습 데이터만 실행(기본값)')
    mode.add_argument('--live',action='store_true',help='실제 CUDA GPU/DB/LLM 연결. 06~08만 지원하며 API 비용 발생 가능')
    args=parser.parse_args()
    hooks={
        "first_relevant_rank":first_relevant_rank,
        "calculate_rr":calculate_rr
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result=execute(4,hooks,live=args.live,level='01_basic')
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure={'status':'execution_failed','exercise':4,
                 'stage':getattr(exc,'stage','evaluation'),
                 'error_type':type(exc).__name__, 'mode':'live' if args.live else 'offline_fixture'}
        write_json(Path(__file__).resolve().parent/'outputs'/'failure.json',failure)
        raise
    output=Path(__file__).resolve().parent/'outputs'/'result.json'
    write_json(output,result)
    # 학생이 코드로 만든 설명 보고서는 별도 Markdown 파일로 저장합니다.
    if isinstance(result.get('markdown_report'),str):
        (output.parent/'report.md').write_text(result['markdown_report'],encoding='utf-8')
    print('Day28 실습 4 · 01_basic ·',result['mode'])
    print('출력:',output)
    return result

if __name__=='__main__':
    main()
