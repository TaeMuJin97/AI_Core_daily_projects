"""
==============================================================================
[실습 보고서: Day 22 실습 05 - 토큰 사용량·지연 시간·비용 정밀 정산 (main.py)]
1. 실험 목적:
   - OpenAI Responses API의 usage 객체 구조(상위 토큰 수 + 하위 details 객체)를 정확히 파싱하고,
     금융/회계 연산 표준인 Decimal을 사용해 100만 토큰당 단가(USD/1M Tokens) 기반 비용을 계산함.
   - 비용 계산만을 위해 불필요한 유료 API를 다시 호출하지 않고, 앞 교시에서 생성된 run.json 로그를
     재활용해 시도(attempt) 단위의 관측 테이블 행(row)을 생성함.
2. 핵심 아키텍처 및 회계 정산 포인트:
   - None(미수신/알 수 없음)과 0(실제 0개 사용)의 엄격한 구분 (D22-05-B01):
     네트워크 오류로 응답이 없거나 usage가 비어 있을 때 `or 0`으로 덮어쓰면,
     '측정 불가(unknown)' 상태가 '무료 호출(0원)'로 왜곡됨. 따라서 u가 없으면 즉시 None을 반환함.
   - 중첩 토큰 산식과 이중 과금 방지 (D22-05-B02):
     1) input_tokens 안에는 이미 cached_tokens가 포함되어 있음. 따라서 일반 단가를 곱할 입력 토큰은
        반드시 `uncached = input_tokens - cached_tokens`로 분리해야 이중 청구를 막을 수 있음.
     2) output_tokens 안에도 이미 reasoning_tokens가 포함되어 있으므로, 출력 비용 계산 시
        reasoning_tokens를 output_tokens에 다시 더하지 않음.
   - 부동소수점(float) 대신 Decimal 사용:
     파이썬 기본 float는 이진 부동소수점 오차(예: 0.1 + 0.2 = 0.30000000000000004)가 발생하므로,
     토큰 단가 같은 소수점 아래 6~8자리 금액 정산에는 반드시 decimal.Decimal을 사용함.
==============================================================================
"""
"""Day22 · 사용량·시간·비용 | PPT 39~46 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from decimal import Decimal as D
from coursekit.support import parse_args, guarded
from coursekit.io import read_json
from coursekit.response import get
from coursekit.metrics import estimate_cost as checkpoint_cost
from coursekit.labs import usage_lab


def usage_of(response):
    # TODO D22-05-B01: 사용량이 없으면 None, 있으면 입력·출력과부분 상세를 읽으세요.
    # 입력·완료 기준: 없는 값에 or0을 쓰지 않습니다. delta 개수를출력 Token 수로쓰지 않습니다.
    # BEGIN D22-05-B01

    # [핵심 포인트 1: 중첩된 usage 구조 파싱 및 None 보존]
    # - response 안에 usage가 없으면 빈 딕셔너리나 0으로 채우지 않고 즉시 None을 반환합니다.
    # - cached_tokens는 u.input_tokens_details 안에, reasoning_tokens는 u.output_tokens_details 안에
    #   중첩되어 있으므로 get(get(u, "..._details"), "..._tokens") 형태로 안전하게 꺼냅니다.
    #   (이미 평탄화된 딕셔너리가 들어오는 경우까지 대비해 u에서도 한 번 더 확인하되, or 0은 절대 쓰지 않습니다.)
    u = get(response, "usage")
    if u is None:
        return None
    in_details = get(u, "input_tokens_details")
    out_details = get(u, "output_tokens_details")
    cached = get(in_details, "cached_tokens") if in_details is not None else get(u, "cached_tokens")
    reasoning = get(out_details, "reasoning_tokens") if out_details is not None else get(u, "reasoning_tokens")
    values = {
        "input_tokens": get(u, "input_tokens"),
        "output_tokens": get(u, "output_tokens"),
        "cached_tokens": cached,
        "reasoning_tokens": reasoning,
        "total_tokens": get(u, "total_tokens"),
    }
    return values
    # END D22-05-B01


def calculate(usage, model, *, service_tier="default"):
    checked = checkpoint_cost(usage, model, service_tier=service_tier)
    if checked["estimated_usd"] is None:
        return checked
    from coursekit.io import ROOT

    price = read_json(ROOT / "config" / "prices.json")["models"][model]
    # TODO D22-05-B02: 캐시를제외한 입력·캐시입력·출력 비용을 Decimal로 계산하세요.
    # 입력·완료 기준: 가격은 USD/100만Token입니다. reasoning을출력에다시더하지 않습니다. unknown과0구분.
    # BEGIN D22-05-B02

    # [핵심 포인트 2: 캐시 제외 입력(uncached) 분리 및 Decimal 정밀 비용 산출]
    # - 전체 입력(i)에서 캐시된 입력(c)을 빼야 일반 단가가 적용될 순수 입력 토큰(uncached)이 됩니다.
    # - 단가표(prices.json)의 가격은 100만(1,000,000) 토큰당 USD 가격이므로,
    #   (일반입력*일반단가 + 캐시입력*캐시단가 + 출력*출력단가) / D(1000000)으로 계산합니다.
    i = usage["input_tokens"]
    c = usage["cached_tokens"]
    o = usage["output_tokens"]
    uncached = i - c
    in_rate = D(str(price["input_per_1m"]))
    cached_rate = D(str(price["cached_input_per_1m"]))
    out_rate = D(str(price["output_per_1m"]))
    amount = (D(uncached) * in_rate + D(c) * cached_rate + D(o) * out_rate) / D(1000000)
    return dict(checked, estimated_usd=str(amount))
    # END D22-05-B02


def make_row(result, attempt, cost):
    # TODO D22-05-B03: 시도번호·실행출처·시간·사용량·비용을 같은 행에 남기세요.
    # 입력·완료 기준: 이 도구는 기존 run.json을 읽습니다. 측정을 위해 필요없는유료재호출은하지 않습니다.
    # BEGIN D22-05-B03

    # [핵심 포인트 3: 시도(attempt)별 시간·사용량·비용 단일 행(Row) 통합]
    # - 상위 result의 식별자(run_id, source_mode)에 더해, 개별 attempt의 전송 번호(send_attempt),
    #   요청 소요 시간(request_ms), 첫 토큰 시간(first_text_ms), 토큰 사용량(usage), 계산된 비용(cost)을 합칩니다.
    usage = attempt.get("usage") or {}
    row = {
        "run_id": result["run_id"],
        "source_mode": result["source_mode"],
        "send_attempt": attempt.get("send_attempt"),
        "request_ms": attempt.get("request_ms"),
        "first_text_ms": attempt.get("first_text_ms"),
        "usage": attempt.get("usage"),
        **usage,
        **(cost or {}),
    }
    return row
    # END D22-05-B03


def main():
    args = parse_args(HERE)
    usage_lab(args, usage_reader=usage_of, calculator=calculate, row_builder=make_row)


if __name__ == "__main__":
    guarded(main)