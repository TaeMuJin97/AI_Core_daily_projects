"""
==============================================================================
[실습 보고서: Day 22 실습 03 - Streaming 수신과 완료 판정 및 TTFT 측정 (main.py)]
1. 실험 목적:
   - OpenAI Responses API의 stream=True 모드를 활성화하여 SSE(Server-Sent Events) 스트림을 수신하고,
     체감 지연 시간 지표인 TTFT(first_text_ms)와 전체 완료 시간(e2e_ms)을 분리 측정함.
   - 텍스트 조각(delta)의 단순 합산과 서버의 공식 완료 판정(Terminal Event)을 엄격히 구분함.
2. 핵심 아키텍처 개념:
   - TTFT (Time To First Token / first_text_ms) 측정 (D22-03-B01):
     요청 시작 시점(started)부터 비어 있지 않은 첫 번째 텍스트 조각(delta)이 도착한 시점(clock())까지의
     시간 차이를 밀리초(ms) 단위로 기록함. 이때 시스템 시간 변경에 영향을 받지 않는 단조 시계(Monotonic Clock,
     time.perf_counter)를 사용하며, 빈 문자열("") delta는 첫 표시로 세지 않음.
   - Delta 개수 != 토큰(Token) 수:
     스트리밍으로 도착하는 delta 조각의 개수나 글자 수는 과금 기준인 입출력 토큰 수와 다름.
     정확한 토큰 사용량(usage)은 반드시 마지막 종료 이벤트의 response 객체에서 읽어야 함.
   - 완료 판정의 권위 (Terminal Event Authority, D22-03-B02):
     부분 문자열(state.parts)이 그럴듯하게 모였다고 해서 클라이언트가 임의로 completed 상태를 만들면,
     네트워크가 중간에 끊기거나 max_output_tokens에 걸려 잘린 불완전한 JSON을 정상 응답으로 오판하게 됨.
     오직 서버가 보낸 종료 이벤트(response.completed, response.incomplete, response.failed)의
     event.response 객체만을 최종 상태(state.final)로 인정하며, 종료 이벤트가 중복 도착하면 오류 처리함.
==============================================================================
"""
"""Day22 · Streaming과 완료 판정 | PPT 24~31 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, execute_case, emit
from coursekit.response import get


def receive_event(state, event, clock, started):
    state.events_seen += 1
    kind = get(event, "type")
    if kind == "response.output_text.delta":
        # TODO D22-03-B01: 비어 있지 않은 첫 텍스트의 시간과 delta를 누적하세요.
        # 입력·완료 기준: clock은 단조 시계입니다. 빈 delta를 첫 표시로 세지 않습니다.
        # BEGIN D22-03-B01

        # [핵심 포인트 1: TTFT(first_text_ms) 최초 1회 기록 및 텍스트 조각 누적]
        # - delta가 빈 문자열("")이 아니고, 아직 first_text_ms가 기록되지 않았다면(is None),
        #   현재 단조 시계(clock())에서 시작 시각(started)을 빼고 1000을 곱해 밀리초(ms)로 저장합니다.
        delta = get(event, "delta", "")
        if delta and state.first_text_ms is None:
            state.first_text_ms = round((clock() - started) * 1000, 3)
        if delta:
            state.parts.append(str(delta))
        # state.parts.append(...)로 누적. delta 개수는 Token 수가 아닙니다.
        # END D22-03-B01
    elif kind in {"response.completed", "response.incomplete", "response.failed"}:
        # TODO D22-03-B02: 최종 이벤트의 Response를 보관하세요.
        # 입력·완료 기준: 부분 문자열을 합쳤다고 completed를 직접 만들어서는 안 됩니다.
        # BEGIN D22-03-B02

        # [핵심 포인트 2: 종료(Terminal) 이벤트 수신 및 중복 종료 방어]
        # - 이미 state.final에 최종 응답이 들어있는데 또 종료 이벤트가 오거나(중복 terminal),
        #   종료 이벤트 안에 response 객체가 없다면 프로토콜 이상이므로 state.error = "stream_error"로 기록합니다.
        # - 정상적인 첫 종료 이벤트라면 state.final에 final_response를 그대로 보관합니다.
        final_response = get(event, "response")
        if state.final is not None or final_response is None:
            state.error = "stream_error"
        else:
            state.final = final_response
        # END D22-03-B02
    elif kind == "error":
        state.error = "stream_error"


def streaming_choice():
    # TODO D22-03-B03: 실제 스트리밍을 요청하도록 선택값을 반환하세요.
    # 입력·완료 기준: 메시지 UI를 새로 만드는 실습이 아닙니다. 최종 상태·부분 파일·first_text_ms를 확인합니다.
    # BEGIN D22-03-B03

    # [핵심 포인트 3: 스트리밍 모드 활성화]
    # - True를 반환하면 execute_case -> run_request 내부에서 stream=True로 Responses API를 호출합니다.
    use_stream = True
    return use_stream
    # END D22-03-B03


def main():
    args = parse_args(HERE)
    modes = [streaming_choice()]
    observations = []
    for use_stream in modes:
        result = execute_case(
            args,
            args.case or "H01",
            stream=use_stream,
            hooks={"event": receive_event},
        )
        emit(args, result)


if __name__ == "__main__":
    guarded(main)