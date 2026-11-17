"""
==============================================================================
[실습 보고서: Day 22 실습 04 - 공급자 API 오류 분류와 제한 재시도 정책 (main.py)]
1. 실험 목적:
   - OpenAI SDK의 암묵적 자동 재시도를 끄고(max_retries=0), 애플리케이션 계층에서 직접
     HTTP 상태 코드(401, 403, 429 등)와 세부 에러 코드(code, error_type)를 분류함.
   - 전송 횟수 상한(2x2=4)과 시간 예산(60초), 그리고 Retry-After 대기 시간을 결합해
     안전한 제한 재시도(Bounded Retry) 정책을 구현함.
2. 핵심 아키텍처 개념:
   - 같은 HTTP 429 안에서의 엄격한 분기 (D22-04-B01):
     HTTP 429(Too Many Requests)는 두 가지 완전히 다른 원인으로 발생함.
     1) insufficient_quota / billing_hard_limit_reached: 크레딧(잔액)이 바닥난 상태.
        기다려도 절대 해결되지 않으므로 retryable=False(kind="quota_error")로 즉시 중단함.
     2) rate_limit_exceeded: 분당 호출 수(RPM)나 토큰 수(TPM)가 일시적으로 몰린 상태.
        잠시 대기하면 풀리므로 retryable=True(kind="rate_limit")로 분류함.
     3) 원인을 알 수 없는 미분류 429는 무조건 재시도하지 않고 안전하게 중단 처리함.
   - 2차원 재시도 한도 (Generation vs Send, D22-04-B02):
     - max_generations=2: 어제(Day 21) 배운 '최초 생성 1회 + 형식 오류 수정(repair) 1회' 한도.
     - max_sends_per_generation=2: 각 생성 단계에서 네트워크 일시 오류나 429 rate_limit 발생 시
       최대 2번까지만 네트워크 전송을 시도함.
     - max_sends_total=4: 최악의 경우에도 한 질문당 총 네트워크 요청이 4번(2x2)을 넘지 못하도록 차단함.
   - 대기 시간(Wait)과 남은 시간 예산(remaining_s) 비교 (D22-04-B03):
     서버가 요구한 최소 대기 시간(Retry-After)이 우리에게 남은 시간 예산(remaining_s)보다 길다면,
     기다려봤자 타임아웃이므로 대기 시간을 임의로 줄이지 않고 None을 반환해 즉시 실행을 중단함.
==============================================================================
"""
"""Day22 · 오류와 제한 재시도 | PPT 32~38 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded
from coursekit.errors import classify_error as checkpoint_classify, retry_delay as checkpoint_delay
from coursekit.runner import RetryPolicy
from coursekit.labs import failure_scenarios


def classify(error):
    # TODO D22-04-B01: 401·403은 중단하고, 429의 quota와 일시적 제한을 구분하세요.
    # 입력·완료 기준: 알 수 없는429는 무조건 재시도하지 않습니다. 실제로 제한을 유발하는 호출은 금지합니다.
    # BEGIN D22-04-B01

    # [핵심 포인트 1: HTTP 상태 코드 및 세부 에러 코드 기반 정밀 분류]
    # - 401(인증 실패)과 403(권한 없음)은 API 키나 프로젝트 권한 문제이므로 기다려도 해결되지 않습니다(retryable=False).
    # - 429는 codes 집합({error.code, error.error_type})을 확인하여 잔액 부족(quota)이면 즉시 중단하고,
    #   명확한 일시적 속도 제한(rate_limit_exceeded / rate_limit_error)일 때만 제한 재시도(retryable=True)를 허용합니다.
    status = error.status
    codes = {error.code, error.error_type}
    if status == 401:
        result = {"kind": "auth_error", "retryable": False}  # 기다려도 키는 바뀌지 않습니다.
    elif status == 403:
        result = {"kind": "permission_error", "retryable": False}
    elif status == 429:
        if codes & {"insufficient_quota", "quota_exceeded", "billing_hard_limit_reached"}:
            result = {"kind": "quota_error", "retryable": False}
        elif codes & {"rate_limit_exceeded", "rate_limit_error", "requests", "tokens"}:
            result = {"kind": "rate_limit", "retryable": True}
        else:
            # 알 수 없는 429는 무조건 재시도하지 않고 기본 분류기(또는 안전한 중단)에 위임합니다.
            result = checkpoint_classify(error)
    else:
        # 그 외 상태 코드(400, 404, 500, 503 등)는 제공된 checkpoint_classify(error)를 이용합니다.
        result = checkpoint_classify(error)
    return result
    # END D22-04-B01


def make_policy():
    # TODO D22-04-B02: 생성 최대2·생성별 전송최대2·전체 전송최대4를 설정하세요.
    # 입력·완료 기준: SDK max_retries=0은 제공 코드에 설정되어 있습니다. 무한 fallback을 추가하지 않습니다.
    # BEGIN D22-04-B02

    # [핵심 포인트 2: 2차원 전송 한도(2x2=4) 및 전체 시간 예산(60초) 설정]
    # - max_generations=2: 최초 응답 생성 1회 + 형식 오류 시 수정 요청(repair) 1회
    # - max_sends_per_generation=2: 각 생성마다 네트워크 전송 최대 2회(최초 전송 1회 + 일시적 오류 재전송 1회)
    # - max_sends_total=4: 전체 누적 네트워크 전송 최대 4회 상한선
    limits = {
        "max_generations": 2,
        "max_sends_per_generation": 2,
        "max_sends_total": 4,
    }
    return RetryPolicy(**limits, elapsed_budget_s=60.0)
    # END D22-04-B02


def delay(attempt, retry_after_s, remaining_s, jitter=0.0):
    # TODO D22-04-B03: 제공된 대기 함수에 남은 예산을 전달하고 반환값을 유지하세요.
    # 입력·완료 기준: 서버의 최소 대기를 짧게 줄이지 않습니다.
    # BEGIN D22-04-B03

    # [핵심 포인트 3: 지수 백오프(Exponential Backoff), Retry-After, 남은 시간 예산 결합]
    # - checkpoint_delay는 서버가 지정한 retry_after_s와 지수 백오프 시간 중 더 안전한 대기 시간을 계산합니다.
    # - 만약 필요한 대기 시간이 남은 시간 예산(remaining_s)을 초과하면 None을 반환해 즉시 중단시키므로,
    #   반환된 wait 값을 임의로 0이나 짧은 숫자로 바꾸지 않고 그대로 유지해 반환합니다.
    wait = checkpoint_delay(attempt, retry_after_s, remaining_s, jitter)
    return wait
    # END D22-04-B03


def main():
    args = parse_args(HERE)
    results = failure_scenarios(args, classifier=classify, delay=delay, policy=make_policy())


if __name__ == "__main__":
    guarded(main)