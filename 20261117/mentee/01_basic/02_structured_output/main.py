"""
==============================================================================
[실습 보고서: Day 22 실습 02 - 메시지와 출력 계약 / Structured Outputs (main.py)]
1. 실험 목적:
   - 지시문(instructions)과 사용자 데이터(input: question + knowledge)의 역할을 명확히 분리하고,
     OpenAI Responses API의 text.format(JSON Schema)을 연결해 서버 측 출력 구조를 강제함.
   - 응답 수신 직후 로컬 Pydantic 검증을 돌리기 전에, API 수준의 거절(refusal)·미완료(status)·빈 본문을
     먼저 걸러내는 1차 관문(response_gate)을 구현함.
2. 핵심 아키텍처 개념:
   - Chat Completions vs Responses API 스키마 지정 방식 차이 (D22-02-B02):
     과거 Chat Completions API는 response_format 파라미터를 썼지만, 최신 Responses API는
     request["text"] = {"format": OUTPUT_FORMAT} 구조로 공급자용 JSON Schema(Wire Schema)를 전달함.
   - Wire Schema vs 로컬 KnowledgeAnswer 검증 분리:
     공급자(OpenAI)의 Structured Outputs는 JSON 문법과 기본 필드 골격만 맞춰줄 뿐,
     source_ids가 실제 제공된 지식 범위(provided_ids) 안에 있는지나 상태 모순 여부는 알지 못함.
     따라서 서버 측 text.format과 로컬 Pydantic + check_rules 검증을 이중으로 결합해야 함.
   - API status vs 비즈니스 status 구분 (D22-02-B03):
     response 객체의 최상위 status("completed", "incomplete" 등)는 API 전송/생성 완료 여부이고,
     모델이 생성한 JSON 안의 status("answered", "insufficient_context")는 질문 답변 가능 여부임.
     모델의 안전 정책 거절(refusal)이나 토큰 상한 잘림(incomplete)을 단순 json_error로 오판해
     불필요한 형식 수정 재시도(repair)를 보내지 않도록 response_gate에서 먼저 분리함.
==============================================================================
"""
"""Day22 · 메시지와 출력 계약 | PPT 14~23 | 01_basic
공통 제공 코드는 교시 독립 시작점입니다. 본 파일의 TODO 함수를 실행 경로에 연결합니다.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

import json
from coursekit.support import parse_args, guarded, execute_case, emit
from coursekit.request import OUTPUT_FORMAT, build_request as checkpoint_request
from coursekit.response import get, output_text


def make_request(model, instructions, question, selected, *, structured=True):
    # TODO D22-02-B01: 질문과 선택 지식만 user input으로 직렬화하세요.
    # 입력·완료 기준: selected_ids가 아닌 선택된 지식의 id·title·content·category를 보냅니다. expected_behavior는 넣지 않습니다.
    # BEGIN D22-02-B01

    # [핵심 포인트 1: 사용자 입력(user input) 페이로드 직렬화]
    # - 지시 규칙은 instructions에 들어가므로, user 메시지에는 순수하게 이번 질문(question)과
    #   선택된 지식 객체 리스트(selected: id, title, content, category 포함)만 담습니다.
    # - 채점 기준인 expected_behavior는 절대 포함하지 않으며, 한글이 유니코드(\uXXXX)로 깨지지 않도록
    #   ensure_ascii=False 옵션을 사용해 JSON 문자열로 직렬화합니다.
    payload = {"question": question, "knowledge": selected}
    serialized = json.dumps(payload, ensure_ascii=False)
    # END D22-02-B01

    # TODO D22-02-B02: 공급자용 Schema를 요청의 text.format으로 연결하세요.
    # 입력·완료 기준: response_format이 아니라 Responses의 text.format입니다. Wire와 로컬 KnowledgeAnswer는 다릅니다.
    # BEGIN D22-02-B02

    # [핵심 포인트 2: 역할 기반 input 배열 및 Responses API 전용 text.format 연결]
    # - 기본 요청 골격을 만든 뒤, input 필드에 role="user"와 직렬화된 문자열(serialized)을 리스트로 넣습니다.
    # - Responses API에서는 response_format 대신 text={"format": OUTPUT_FORMAT}에 JSON Schema를 지정합니다.
    request = checkpoint_request(model, instructions, question, selected, structured=False)
    request["input"] = [{"role": "user", "content": serialized}]
    if structured:
        request["text"] = {"format": OUTPUT_FORMAT}
    return request
    # END D22-02-B02


def response_gate(response):
    # TODO D22-02-B03: 거절 콘텐츠와 미완료 상태를 먼저 구분하세요.
    # 입력·완료 기준: API status와 answer JSON의 status는 다릅니다. 거절을 형식 오류로 바꾸지 않습니다.
    # BEGIN D22-02-B03

    # [핵심 포인트 3: 공급자 안전 거절(refusal) 및 API 미완료 상태 사전 차단]
    # - get(객체, 키, 기본값) 헬퍼 함수는 SDK 응답 객체(Attribute)와 일반 dict(Key) 모두에서 안전하게 값을 꺼냅니다.
    # - 1) output 배열 안의 message 파트 중에 type=="refusal"이거나 refusal 텍스트가 존재하면,
    #      모델이 안전 정책상 답변을 거부한 것이므로 JSON 형식 오류로 취급하지 않고 즉시 (None, "refused")를 반환합니다.
    for item in get(response, "output", []) or []:
        if get(item, "type") == "message":
            for part in get(item, "content", []) or []:
                if get(part, "type") == "refusal" or get(part, "refusal"):
                    return None, "refused"

    # - 2) API 응답 자체의 생성 상태(status)가 "completed"가 아니라면(예: max_output_tokens 도달로 인한 "incomplete" 등),
    #      깨진 JSON을 파싱하기 전에 해당 상태를 그대로 오류 코드로 반환합니다.
    status = get(response, "status")
    if status != "completed":
        return None, status or "incomplete"
    # END D22-02-B03

    # TODO D22-02-B04: 완료 응답에서도 빈 본문을 검사한 뒤 원문을 반환하세요.
    # 입력·완료 기준: 원문을 수정해 유효한 JSON처럼 만들지 않습니다. 로컬 검증기는 다음 단계에서 실행됩니다.
    # BEGIN D22-02-B04

    # [핵심 포인트 4: 완료된 응답의 빈 본문(empty_output) 방어]
    # - status가 "completed"여도 추출한 텍스트 본문(raw)이 없거나 공백뿐이면 (None, "empty_output")을 반환합니다.
    # - 본문이 존재하면 임의로 문자열을 다듬지 않고 날것의 원문 그대로 (raw, None)을 반환해 다음 단계(로컬 Pydantic 검증기)로 넘깁니다.
    raw = output_text(response)
    if not raw or not raw.strip():
        return None, "empty_output"
    return raw, None
    # END D22-02-B04


def main():
    args = parse_args(HERE)
    cases = ["D02"]
    for case_id in ([args.case] if args.case else cases):
        result = execute_case(
            args,
            case_id,
            request_builder=make_request,
            hooks={"gate": response_gate},
        )
        emit(args, result)
        if result["run_status"] in {"auth_error", "quota_error", "permission_error", "not_run"}:
            break


if __name__ == "__main__":
    guarded(main)