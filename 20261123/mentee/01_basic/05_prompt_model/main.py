"""실습 05 · Prompt 구성과 Chat Model 호출을 구분합니다."""
from pathlib import Path
import argparse
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 폴더에서 실행해도 현재 역할 폴더의 coursekit을 import하도록 연결
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from coursekit.data import example_hit, load_hits
from coursekit.checkpoints import make_prompt           # system(규칙) + human({question}, {context}) 템플릿 생성기
from coursekit.llm import create_chat_model             # 실제 OpenAI ChatOpenAI 생성기 (호출 시 .env 필요)
from coursekit.fixtures import fixture_chat_model, fixture_generation  # 오프라인 테스트용 가짜 모델
from coursekit.reporting import execution_record, message_record
from coursekit.io import save_json, show_success


def make_inputs(question: str, context: str) -> dict:
    """입력: 질문·근거 문자열 / 출력: question, context 두 Key를 가진 dict."""
    # BEGIN D26-05-B01
    # [흐름 이해: 템플릿 변수 이름 맞추기]
    # coursekit/checkpoints.py의 make_prompt() 안에는
    #   ("human", "질문:\n{question}\n\n자료:\n{context}")
    # 처럼 두 개의 빈칸({question}, {context})이 뚫려 있습니다.
    # 따라서 prompt.invoke()에 넘길 dict의 Key 이름도 반드시 "question", "context"로 정확히 일치시켜야 합니다!
    return {
        "question": question,  # 사용자가 물어본 질문 문자열
        "context": context,    # 출처 ID·원문 위치·본문이 합쳐진 참고 자료 문자열
    }
    # END D26-05-B01


def invoke_pair(prompt, chat_model, inputs: dict):
    """dict → ChatPromptValue → AIMessage. 반환: (prompt_value, message)."""
    # BEGIN D26-05-B02
    # [흐름 이해: 같은 .invoke()라도 1단계와 2단계의 역할이 완전히 다릅니다!]
    #
    # 1단계) Prompt 실행 (로컬 작업 · API 비용 0원)
    #   - inputs({"question": ..., "context": ...})를 템플릿 빈칸에 채워 넣습니다.
    #   - 반환값 prompt_value는 system/human 메시지가 담긴 'ChatPromptValue' 객체입니다.
    prompt_value = prompt.invoke(inputs)

    # 2단계) Chat Model 실행 (실제 모드에서는 외부 LLM API 요청 · 비용 발생 지점!)
    #   - 1단계의 출력(prompt_value)을 그대로 모델의 입력으로 넘깁니다.
    #   - 반환값 message는 모델의 응답 텍스트와 메타데이터가 담긴 'AIMessage' 객체입니다.
    message = chat_model.invoke(prompt_value)

    # 모델에 '보내기 전 입력(prompt_value)'과 '받은 뒤 응답(message)'을 나란히 비교할 수 있도록
    # 튜플 (prompt_value, message) 순서로 반환합니다.
    return prompt_value, message
    # END D26-05-B02


def context_of(hit: dict) -> str:
    """앞 장에서 배운 출처 포함 블록 형식입니다. 이번 실습의 제공 코드입니다."""
    return f'[{hit["citation_id"]}] {hit["source_locator"]}\n{hit["body"]}'


def main():
    # 1) 실행 옵션: --offline을 주면 가짜 모델(비용 0원), 빼면 실제 OpenAI API 호출
    parser = argparse.ArgumentParser(description="Prompt → Chat Model 입력·출력 관찰")
    parser.add_argument("--offline", action="store_true", help="고정 응답 예시만 사용; 실제 모델 미실행")
    args = parser.parse_args()

    # 2) 출석 규정 예시 1건과 공통 ChatPromptTemplate 준비
    attendance = example_hit()
    prompt = make_prompt()
    cases = [("attendance_15", "15분 늦으면 어떻게 기록되나요?", attendance)]

    # 3) [좋은 설계 습관] 모델 객체를 만들거나 유료 API를 부르기 전에,
    #    로컬 TODO(make_inputs)와 입력 데이터부터 먼저 준비·검증해 실패 시 불필요한 비용을 막습니다.
    prepared = [
        (case_id, make_inputs(question, context_of(hit)), hit)
        for case_id, question, hit in cases
    ]
    observations = {}

    # 4) 모델 선택: 기본 경로는 실제 모델(create_chat_model)이며,
    #    환경 설정 오류 시 자동으로 가짜 예시로 덮어쓰지 않고 오류를 그대로 드러냅니다.
    chat_model = fixture_chat_model() if args.offline else create_chat_model()

    # 5) 각 케이스 실행 및 [입력 메시지 vs 모델 응답 vs 원문 근거] 기록
    records = []
    for case_id, inputs, hit in prepared:
        prompt_value, message = invoke_pair(prompt, chat_model, inputs)
        records.append({
            "case_id": case_id,
            "question": inputs["question"],
            "context": inputs["context"],
            "prompt_value_type": type(prompt_value).__name__,          # 기대값: "ChatPromptValue"
            "prompt_messages": [
                {"type": m.type, "content": m.content}                 # 기대 역할: "system", "human"
                for m in prompt_value.to_messages()
            ],
            "response": message_record(message),                       # 기대 type: "AIMessage"
            "evidence": {
                "citation_id": hit["citation_id"],
                "doc_id": hit["doc_id"],
                "source_locator": hit["source_locator"],
                "body": hit["body"],
            },
            # 모델이 답을 돌려줬다고 사실 일치(Grounding)가 보장되지 않으므로 사람이 대조하기 전까지 pending!
            "human_evidence_review": "pending",
        })

    # 6) 실행 모드(offline_fixture vs live)와 실제 호출 횟수를 투명하게 JSON으로 저장
    result = {
        "exercise": "05_prompt_model",
        "execution": execution_record("offline_fixture" if args.offline else "live", llm=not args.offline),
        "real_model_calls": 0 if args.offline else len(records),
        "fixed_example_calls": len(records) if args.offline else 0,
        "observations": observations,
        "cases": records,
        "review_note": "문장·출처의 정답 여부는 자동 판정하지 않았습니다. reports/review.md에 원문 대조를 기록하세요.",
    }
    path = save_json(HERE, "prompt_model.json", result)
    show_success("05 Prompt·Chat Model 관찰 기록", path)
    print("실제 LLM 실행:", not args.offline, "| 원문 대조: 수강생 확인 필요")


if __name__ == "__main__":
    main()