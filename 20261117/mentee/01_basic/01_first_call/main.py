"""
==============================================================================
[실습 보고서: Day 22 실습 01 - OpenAI Responses API 첫 실제 응답 연결 (main.py)]
1. 실험 목적:
   - API 키를 코드에 하드코딩하지 않고 환경변수(.env)에서 안전하게 주입받아,
     OpenAI Responses API(client.responses.create)로 첫 요청을 전송하고 응답 메타데이터를 기록함.
2. 핵심 아키텍처 및 파이썬 문법 포인트:
   - 키워드 전용 인자 (*, structured=False):
     함수 정의에서 * 뒤에 오는 매개변수는 위치 인자로 넘길 수 없고 반드시 structured=True 처럼
     이름을 명시해서만 호출할 수 있게 강제하는 문법으로, 플래그 인자 전달 실수를 방지함.
   - 딕셔너리 언패킹 호출 (**options):
     요청 파라미터들을 딕셔너리(request)로 조립해 둔 뒤, API 호출 시점에 **options로 펼쳐서
     client.responses.create(model=..., instructions=..., ...) 형태의 키워드 인자로 전달함.
   - 안전한 중첩 데이터 추출과 미실행(None) 보존:
     실제 API 호출 전이거나 미실행 상태일 때 가짜 응답 ID(0이나 빈 문자열)를 넣지 않고
     None 그대로 유지하여 연결 상태를 정직하게 기록함.
==============================================================================
"""
"""Day22 · 첫 실제 응답 | PPT 6~13 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.support import parse_args, guarded, execute_case, emit
from coursekit.io import write_json


def make_first_request(model, instructions, question, selected, *, structured=False):
    # TODO D22-01-B01: 첫 요청의 model·instructions·input·출력 상한·store를 완성하세요.
    # 입력·완료 기준: 입력은 전달받은 값입니다. 새 질문·임의 모델을 하드코딩하지 않으며 JSON Schema는 다음 교시입니다.
    # BEGIN D22-01-B01

    # [핵심 포인트 1: Responses API 기본 요청 페이로드 조립]
    # - model, instructions, question은 외부(설정 및 케이스 데이터)에서 주입받은 변수를 그대로 연결합니다.
    # - max_output_tokens: 1200으로 출력 토큰 상한선을 지정해 비용과 응답 길이를 통제합니다.
    # - store: False로 설정하여 실습 요청 데이터가 원격 서버에 기본 저장되지 않도록 제어합니다.
    request = {
        "model": model,
        "instructions": instructions,
        "input": question,
        "reasoning": {"effort": "none"},
        "max_output_tokens": 1200,
        "store": False,
        "service_tier": "default",
    }
    return request
    # END D22-01-B01


def create_response(client, request, stream=False):
    # TODO D22-01-B02: Responses API를 한 번 호출하고 반환값을 돌려주세요.
    # 입력·완료 기준: 키를 직접 문자열로 쓰지 않습니다. 한 함수 호출은 create 한 번만 수행합니다.
    # BEGIN D22-01-B02

    # [핵심 포인트 2: 딕셔너리 복사 및 ** 언패킹을 통한 SDK 호출]
    # - 원본 request 딕셔너리가 훼손되지 않도록 dict(request)로 얕은 복사본을 만듭니다.
    # - **options 문법은 딕셔너리의 키-값 쌍을 함수의 키워드 인자(key=value)로 풀어서 전달합니다.
    options = dict(request)
    response = client.responses.create(**options, stream=stream)
    return response
    # END D22-01-B02


def make_view(result):
    # TODO D22-01-B03: 키 없이 source·model·종료 상태·응답 ID를 요약하세요.
    # 입력·완료 기준: 미실행이면 response_id는 None입니다. 0이나 가짜 응답 ID를 채우지 않습니다.
    # BEGIN D22-01-B03

    # [핵심 포인트 3: 실행 결과 및 마지막 시도(last)에서 안전하게 상태 추출]
    # - attempts 리스트가 비어 있지 않다면 가장 마지막 시도 기록([-1])을 가져오고, 비어 있다면 빈 딕셔너리({})를 씁니다.
    # - API 키는 로그나 요약 파일(connection_view.json)에 절대 남기지 않고,
    #   실행 모드(source_mode), 모델명(model), 실행 상태(run_status), 고유 응답 ID(response_id)만 추출합니다.
    last = result.get("attempts", [])[-1] if result.get("attempts") else {}
    summary = {
        "source_mode": result.get("source_mode"),
        "model": result.get("model", last.get("model")),
        "run_status": result.get("run_status", last.get("run_status")),
        "response_id": last.get("response_id", result.get("response_id")),
    }
    return summary
    # END D22-01-B03


def main():
    args = parse_args(HERE)
    result = execute_case(
        args,
        "FIRST",
        request_builder=make_first_request,
        hooks={"create": create_response},
    )
    emit(args, result)
    view = make_view(result)
    write_json(args.output_dir / "connection_view.json", view)


if __name__ == "__main__":
    guarded(main)