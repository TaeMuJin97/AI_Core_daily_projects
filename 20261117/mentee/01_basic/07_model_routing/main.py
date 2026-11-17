"""
==============================================================================
[실습 보고서: Day 22 실습 07 - 명시적 모델 라우팅(Model Routing)과 공통 결과 계약 (main.py)]
1. 실험 목적:
   - 호출 전에 실행 모드(fast / quality)에 따라 허용된 모델을 선택하고, 선택 이유(route_reason)를
     실행 기록에 남기는 명시적 라우팅(Model Routing) 정책을 구현함.
   - 모델이 바뀌더라도 동일한 입력 프롬프트·출력 스키마(KnowledgeAnswer)·관측 필드(record_view)를
     유지하여 공정한 비교 기반을 마련함.
2. 핵심 아키텍처 개념:
   - Routing(호출 전 선택) vs Fallback(실패 후 자동 전환)의 분리 (D22-07-B01, B03):
     Routing은 요청을 보내기 전에 조건과 모드에 맞는 모델을 고르는 정책임.
     반면 알 수 없는 모드(예: "ultra")가 들어왔을 때 조용히 "fast"로 바꿔치기(Silent Fallback)하거나,
     정보 부족(insufficient_context)·안전 거절(refused)이 나왔다고 해서 while 루프로 더 비싼 모델에
     자동 재전송하면 예산 폭발과 정책 우회 사고가 발생함. 따라서 미지원 모드는 호출 전 ValueError로 차단함.
   - 실행 결과(run_status)와 업무 답변(answer_object.status)의 결합 기록 (D22-07-B02):
     모델이 달라도 반환 구조(fields 10개)는 완벽히 동일해야 함.
     고가 모델(quality)이라고 해서 자동으로 더 높은 점수를 주거나 evidence_ok=True를 채우지 않으며,
     권한이 없거나 비교를 실행하지 않은 경우 정직하게 not_run 상태로 기록함.
==============================================================================
"""
"""Day22 · 명시적 모델 선택 | PPT 53~59 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded
from coursekit.config import choose_model as checkpoint_choose
from coursekit.labs import routing_lab


def route(mode, models):
    # TODO D22-07-B01: fast·quality만허용하고실제모델과선택이유를반환하세요.
    # 입력·완료 기준: 알수없는모드를fast로조용히바꾸지않습니다. quality권한없으면not_run입니다.
    # BEGIN D22-07-B01

    # [핵심 포인트 1: 허용 모드 화이트리스트 검사 및 선택 이유(route_reason) 반환]
    # - allowed 집합({"fast", "quality"})에 없는 모드가 들어오면 조용히 기본값으로 덮어쓰지 않고
    #   즉시 ValueError를 발생시켜 잘못된 설정이 API 호출로 이어지는 것을 막습니다.
    # - checkpoint_choose(mode, models)를 통해 설정된 모델 ID와 "explicit_mode:<mode>" 사유를 함께 반환합니다.
    allowed = {"fast", "quality"}
    if mode not in allowed:
        raise ValueError(f"지원하지 않는 실행 모드입니다: {mode}")
    model, reason = checkpoint_choose(mode, models)
    return (model, reason)
    # END D22-07-B01


def record_view(result):
    # TODO D22-07-B02: 어떤모델이든동일한결과필드로비교하세요.
    # 입력·완료 기준: 고가모델이항상더좋다는결론을미리넣지않습니다.
    # BEGIN D22-07-B02

    # [핵심 포인트 2: 모델 무관 단일 결과 계약(Common Result Contract) 추출]
    # - fast 모델을 쓰든 quality 모델을 쓰든, 혹은 미실행(not_run)이든 동일한 10개 필드로 행을 구성합니다.
    # - 실행 상태(run_status)와 업무 답변 객체(answer_object), 사람 검토 여부(evidence_ok),
    #   사용량(usage)·시간(request_ms)·추정 비용(estimated_usd)을 한눈에 대조할 수 있게 정리합니다.
    fields = [
        "case_id",
        "source_mode",
        "model",
        "route_reason",
        "run_status",
        "answer_object",
        "evidence_ok",
        "usage",
        "request_ms",
        "estimated_usd",
    ]
    row = {key: result.get(key) for key in fields}
    return row
    # END D22-07-B02


def comparison_modes():
    # TODO D22-07-B03: 명시적비교에서만fast·quality를한번씩선택하세요.
    # 입력·완료 기준: 기본run은한모델만호출합니다. compare는계정권한·예산확인후선택합니다.
    # BEGIN D22-07-B03

    # [핵심 포인트 3: 명시적 비교(--action compare) 대상 모드 목록 정의]
    # - 기본 실행(--action run)은 지정한 단일 모드(기본 fast) 1개만 호출합니다.
    # - 사용자가 명시적으로 비교(--action compare)를 요청했을 때만 fast와 quality를 순서대로 1번씩 실행합니다.
    modes = ["fast", "quality"]
    return modes
    # END D22-07-B03


def main():
    args = parse_args(HERE)
    routing_lab(args, router=route, record_view=record_view, compare_modes=comparison_modes)


if __name__ == "__main__":
    guarded(main)