"""
==============================================================================
[실습 보고서: Day 22 실습 08 - AI 지식 답변 생성기 v2 통합 및 회귀 검증 (main.py)]
1. 실험 목적:
   - Day 21에서 고정한 입력 프롬프트·지식 스냅샷(101~103)·출력 계약(KnowledgeAnswer) 위에
     오늘 구현한 OpenAI Responses API 호출·스트리밍·오류 제어·비용 정산·응답 캐시·모델 라우팅을
     하나로 통합하여 H01~H03 질문을 끝까지 연결함.
2. 핵심 아키텍처 개념:
   - Holdout(H01~H03)의 오늘자 역할 변화 (Regression & Integration Check, D22-08-B01):
     어제(Day 21) 이미 H01~H03 질문을 확인했으므로, 오늘 다시 호출하는 것은 '처음 보는 미사용 데이터에 대한
     일반화 성능 평가'가 아니라 '수동 응답을 API 클라이언트로 교체한 뒤에도 기존 계약이 깨지지 않고
     연동되는지 확인하는 회귀(Regression)·통합 테스트'임.
     * H01: stream=True(스트리밍) 경로로 실행하여 first_text_ms와 완료 판정을 검증함.
     * H02: 비밀번호 질문(지식 102에 없음)으로 completed + insufficient_context 정상 조합을 확인함.
     * H03: 다중 지식(101, 102, 103) 요약 및 실제 출처 인용을 확인함.
   - 관측 무결성과 서킷 브레이커 (D22-08-B02, B03):
     중간에 401/403/quota_error 등이 발생하면 daily_project가 즉시 후속 질문 호출을 멈추고(not_run),
     table_rows와 summarize_runs를 통해 성공·실패·모의·캐시·미실행을 누락 없이 분리 기록함.
   - 불변 조건(Invariant) 자동 검증 (D22-08-B04):
     자동 검증을 통과했더라도 사람의 근거 대조(tools/review.py) 전에는 evidence_ok가 반드시 None이어야 하며,
     어떤 경우에도 질문당 신규 API 전송 횟수(new_api_send_count)는 상한선인 4회를 넘지 않음을 assert로 보증함.
==============================================================================
"""
"""Day22 · AI 지식 답변 생성기 v2 | PPT 60~68 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, daily_project
from coursekit.metrics import summarize_runs
from coursekit.records import table_rows


def project_cases():
    # TODO D22-08-B01: 최종연동확인질문H01·H02·H03을같은순서로지정하세요.
    # 입력·완료 기준: 이미본질문이므로새holdout의일반화성능이라고부르지않습니다.
    # BEGIN D22-08-B01

    # [핵심 포인트 1: 회귀·연동 확인용 케이스 순서 지정]
    # - H01(오류 질문 작성 안내, 스트리밍), H02(서버 비밀번호, 정보 부족), H03(세 안내 종합 요약)을 순서대로 지정합니다.
    cases = ["H01", "H02", "H03"]
    return cases
    # END D22-08-B01


def project_rows(runs):
    # TODO D22-08-B02: 각실행의상태·사용량·시간을표행으로연결하세요.
    # 입력·완료 기준: 실패한행도버리지않습니다. 모든질문의예상답을실측답으로채우지않습니다.
    # BEGIN D22-08-B02

    # [핵심 포인트 2: 실행 결과 리스트를 관측 테이블 행(observations.csv용)으로 변환]
    # - table_rows(runs)를 호출해 각 질문의 source_mode, run_status, 지연 시간, 토큰 사용량, 추정 비용을 추출합니다.
    rows = table_rows(runs)
    return rows
    # END D22-08-B02


def project_summary(runs):
    # TODO D22-08-B03: 실제·모의·캐시·미실행을분리하여요약하세요.
    # 입력·완료 기준: 소수관찰로P95·SLA·보편적모델우열을주장하지않습니다.
    # BEGIN D22-08-B03

    # [핵심 포인트 3: 출처(api_live / simulated / app_cache / not_run)별 분리 요약]
    # - summarize_runs(runs)를 통해 관측된 비용 합계, 미확인(unknown) 건수, 출처별 건수를 정직하게 요약합니다.
    summary = summarize_runs(runs)
    return summary
    # END D22-08-B03


def check_project(runs):
    # TODO D22-08-B04: 자동검사후사람미평가None을유지하고전송상한을확인하세요.
    # 입력·완료 기준: 사람평가는tools/review.py의별도파일로남깁니다. 새API·DB·RAG는만들지않습니다.
    # BEGIN D22-08-B04

    # [핵심 포인트 4: 파이프라인 핵심 안전 불변 조건(Invariants) 검증]
    # - 1) 자동 검증 통과만으로는 근거 정합성이 증명되지 않으므로, 별도 review.py 승인 전까지 evidence_ok는 None이어야 합니다.
    # - 2) 2차원 재시도 예산(생성 최대 2회 x 전송 최대 2회)에 의해 질문당 신규 API 전송 수(sends)는 절대 4를 넘을 수 없습니다.
    for run in runs:
        evidence = run.get("evidence_ok")  # 사람 평가 전 None
        sends = run.get("new_api_send_count", 0)
        assert evidence is None, f"사람 검토 전 evidence_ok는 None이어야 합니다: {evidence}"
        assert 0 <= sends <= 4, f"전송 상한(최대 4회) 위반: {sends}"
    # END D22-08-B04


def main():
    args = parse_args(HERE)
    runs = daily_project(
        args,
        prepare_cases=project_cases,
        make_table=project_rows,
        finish_summary=project_summary,
    )
    if isinstance(runs, list):
        check_project(runs)


if __name__ == "__main__":
    guarded(main)