"""Day28 실습 08 · 01_basic · 실행 진입점.
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


def evaluate_one(example: dict, run: dict, gold: list[str], grades: dict) -> dict:
    """질문 ID로 Target 출력과 Gold를 결합해 평가 레코드를 반환하세요."""
    # 정답 D28-08-B01: 질문 ID로 Target 출력과 Gold를 결합해 평가 레코드를 반환하세요.
    # 절차: Trace 필드가 빠졌다면 빈 리스트로 바꾸지 말고 오류로 보고합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_report import evaluate_record
    return evaluate_record(example,run,gold,grades,k=3)

def summarize_all(rows: list[dict]) -> dict:
    """개별 질문 결과의 평균(유효 Gold만)과 오류·출처 상태를 집계하세요."""
    # 정답 D28-08-B02: 개별 질문 결과의 평균(유효 Gold만)과 오류·출처 상태를 집계하세요.
    # 절차: No-answer 질문은 Retrieval 평균에서 제외하고 별도 개수로 기록합니다.
    # 이 구현은 모델·DB를 호출하지 않는 규칙 / 또는 필요한 함수에 위임하는 부분입니다.
    from coursekit.eval_report import report_summary
    return report_summary(rows)


def main():
    parser=argparse.ArgumentParser(description="Day28 RAG Evaluation 실습")
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--offline',action='store_true',help='고정 학습 데이터만 실행(기본값)')
    mode.add_argument('--live',action='store_true',help='실제 CUDA GPU/DB/LLM 연결. 06~08만 지원하며 API 비용 발생 가능')
    args=parser.parse_args()
    hooks={
        "evaluate_one":evaluate_one,
        "summarize_all":summarize_all
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result=execute(8,hooks,live=args.live,level='01_basic')
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure={'status':'execution_failed','exercise':8,
                 'stage':getattr(exc,'stage','evaluation'),
                 'error_type':type(exc).__name__, 'mode':'live' if args.live else 'offline_fixture'}
        write_json(Path(__file__).resolve().parent/'outputs'/'failure.json',failure)
        raise
    output=Path(__file__).resolve().parent/'outputs'/'result.json'
    write_json(output,result)
    # 학생이 코드로 만든 설명 보고서는 별도 Markdown 파일로 저장합니다.
    if isinstance(result.get('markdown_report'),str):
        (output.parent/'report.md').write_text(result['markdown_report'],encoding='utf-8')
    print('Day28 실습 8 · 01_basic ·',result['mode'])
    print('출력:',output)
    return result

if __name__=='__main__':
    main()
