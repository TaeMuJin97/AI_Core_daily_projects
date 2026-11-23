"""실습 06 · Context·출처를 보관하고 Runnable Chain을 실행합니다."""
from pathlib import Path
import argparse
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 폴더에서 실행해도 현재 역할 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from coursekit.data import load_hits
from coursekit.checkpoints import (
    hits_to_documents,  # Hit 목록 → LangChain Document 목록 변환기 (4교시 완성품)
    build_context,      # 중복 제거 + 글자 예산 + 개수 제한 Context 빌더
    make_prompt,        # system(규칙) + human({question}, {context}) 템플릿 생성기
    WireAnswer,         # LLM에게 강제할 4필드(status, answer, source_ids, missing_information) 스키마
)
from coursekit.llm import create_chat_model          # 실제 OpenAI ChatOpenAI 생성기
from coursekit.fixtures import fixture_generation    # 오프라인 테스트용 고정 bundle 생성기 (비용 0원)
from coursekit.reporting import execution_record, bundle_record
from coursekit.io import save_json, show_success


def prepare_context(documents, question: str, max_items=2, max_chars=600) -> dict:
    """Document 목록 → Context·포함 문서·포함 ID·Prompt 입력. 원문은 바꾸지 않습니다."""
    # BEGIN D26-06-B01
    # [흐름 이해: Context 생성과 '실제 포함 출처 ID'를 한 묶음으로 확정하기]
    #
    # 1) build_context() 호출:
    #    - 중복 chunk_id를 건너뛰고, max_chars(600자) 예산과 max_items(2개) 상한 안에서
    #      실제로 모델에게 보여줄 문자열(context)과 선택된 문서 목록(included_docs)을 함께 돌려받습니다.
    context, included_docs = build_context(
        documents,
        max_items=max_items,
        max_chars=max_chars,
    )

    # 2) 허용 출처 ID(provided_ids) 추출:
    #    - 주의! 전체 후보(documents)가 아니라 실제 Context에 들어간 'included_docs'에서만 꺼내야 합니다.
    #    - main()에서 이 값을 그대로 JSON 파일로 저장하므로, set이 아닌 list[int] 형태로 보관합니다.
    provided_ids = [doc.metadata["citation_id"] for doc in included_docs]

    # 3) Prompt에 넘길 입력 딕셔너리(inputs) 구성:
    #    - make_prompt()의 변수 이름({question}, {context})과 정확히 일치시킵니다.
    inputs = {
        "question": question,
        "context": context,
    }

    # 4) 다음 단계(Chain 실행 + 출처 검증·기록)에서 각각 꺼내 쓸 수 있도록 4개 Key로 묶어 반환합니다.
    return {
        "context": context,              # 모델에 실제로 전달될 최종 Context 문자열
        "included_docs": included_docs,  # 실제 포함된 Document 객체 목록 (원문 메타데이터 보관용)
        "provided_ids": provided_ids,    # 실제 포함된 정수 citation_id 목록 (예: [201, 202])
        "inputs": inputs,                # prompt | structured_model 체인에 넣을 입력 dict
    }
    # END D26-06-B01


def run_generation(prompt, structured_model, inputs: dict):
    """Prompt → Structured Model의 bundle. bundle 검증·승인은 다음 실습입니다."""
    # BEGIN D26-06-B02
    # [흐름 이해: LCEL 파이프(|)로 두 Runnable을 하나의 Chain으로 연결해 실행하기]
    #
    # 1) 파이프(|)로 순서 조립 (이 줄에서는 아직 실행되지 않음 · API 비용 0원):
    #    - 앞 단계(prompt)의 출력(ChatPromptValue)이
    #      자동으로 뒤 단계(structured_model)의 입력으로 흘러가도록 연결합니다.
    chain = prompt | structured_model

    # 2) invoke(inputs)로 전체 Chain 실행:
    #    - inputs(dict) → prompt → ChatPromptValue → structured_model → bundle(dict)
    #    - 반환된 bundle은 {"raw": AIMessage, "parsed": WireAnswer | None, "parsing_error": ...} 구조입니다.
    #    - 실제 실행에서 오류나 거절이 생겨도 값을 임의로 고치지 않고 bundle을 있는 그대로 반환합니다!
    bundle = chain.invoke(inputs)
    return bundle
    # END D26-06-B02


def main():
    # 1) 실행 옵션: 개발·검증은 --offline(비용 0원) 먼저, 최종 실측만 기본 실행(python main.py)
    parser = argparse.ArgumentParser(description="Context → Prompt → Structured Model 관찰")
    parser.add_argument("--offline", action="store_true", help="고정 bundle 예시만 사용; 실제 모델 미실행")
    args = parser.parse_args()

    # 2) '학사' 카테고리 예시 Hit 2건(출석 201, 과제 202)을 Document 목록으로 변환
    academic_hits = [hit for hit in load_hits() if hit["category"] == "학사"]
    documents = hits_to_documents(academic_hits)
    question = "15분 늦으면 어떻게 기록되나요?"

    # 3) [1단계 TODO] Context·포함 문서·포함 ID·Prompt 입력을 한 번에 준비
    prepared = prepare_context(documents, question)
    experiments = {}
    prompt = make_prompt()

    # 4) 모델 준비: 아직 API를 호출하지 않고 설정 객체만 준비합니다.
    if args.offline:
        # 오프라인 모드: 실제 모델과 동일한 3키(raw, parsed, parsing_error) bundle을 주는 가짜 Runnable
        structured_model = fixture_generation()
    else:
        # 라이브 모드: Responses API + Strict JSON Schema(WireAnswer) + 원본(raw) 함께 반환 설정
        chat_model = create_chat_model()
        structured_model = chat_model.with_structured_output(
            WireAnswer,
            method="json_schema",
            strict=True,
            include_raw=True,
        )

    # 5) [2단계 TODO] prompt | structured_model 체인을 실행해 bundle 수신
    bundle = run_generation(prompt, structured_model, prepared["inputs"])
    if bundle is None:
        raise AssertionError("이번 정상 예시의 Context는 비어 있지 않아야 합니다.")

    # 6) 파싱 결과에서 모델이 인용한 source_ids 관찰 (단, 승인 검증은 7교시에서 별도 수행!)
    parsed = bundle.get("parsed")
    cited_ids = list(parsed.source_ids) if parsed is not None else []

    # 7) Context·포함 출처·bundle·ID 포함 여부 관찰값을 JSON으로 저장
    result = {
        "exercise": "06_context_chain",
        "execution": execution_record("offline_fixture" if args.offline else "live", llm=not args.offline),
        "real_model_calls": 0 if args.offline else 1,
        "context": prepared["context"],
        "included_ids": prepared["provided_ids"],
        "included_sources": [dict(doc.metadata) for doc in prepared["included_docs"]],
        "prompt_input": prepared["inputs"],
        "bundle": bundle_record(bundle),
        "observed_source_ids": cited_ids,
        "source_id_membership_only": None if parsed is None else set(cited_ids).issubset(prepared["provided_ids"]),
        "experiments": experiments,
        "human_evidence_review": "pending",
        "review_note": "bundle·포함 ID를 관찰한 기록입니다. 자료형·상태·출처의 승인 검사는 실습07에서 진행합니다.",
    }
    path = save_json(HERE, "context_chain.json", result)
    show_success("06 Context·Runnable 관찰 기록", path)
    print("실제 LLM 실행:", not args.offline, "| 검증 승인 전 bundle 관찰")


if __name__ == "__main__":
    main()