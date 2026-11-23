"""Day26 실습 7 · 기본필수. 실행 위치와 무관하게 현재 역할 폴더를 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))

from coursekit.io import save_json, show_success
from coursekit.data import example_hit
from coursekit.checkpoints import (
    hits_to_documents,  # Hit 목록 → LangChain Document 목록 변환기
    build_context,      # Context 본문 + 실제 포함된 Document 목록(included_docs) 반환
    NO_ANSWER,          # "제공된 지식으로는 답할 수 없습니다." 고정 문구 상수
    RagServiceError,    # 검증·실행 실패 시 서버가 던지는 전용 예외 클래스
    receive_bundle,     # raw → parsing_error → parsed → 업무·출처 규칙 4단계 검문 함수
)
from coursekit.fixtures import fixture_bundle      # 테스트용 고정 bundle(raw/parsed/parsing_error) 생성기
from coursekit.reporting import execution_record


def common_cases():
    """의도적으로 만든 세 입력입니다. 실제 모델의 응답 로그가 아닙니다."""
    # [사례 1: 정상 답변] 출석 v2(ID=201) 근거를 인용하고 missing_information을 비움
    answered = {
        "status": "answered",
        "answer": "일반 기준으로 15분까지는 지각입니다. 사전 승인을 받았다면 운영실에 확인합니다.",
        "source_ids": [201],
        "missing_information": "",
    }
    # [사례 2: 정상 정보 부족] 근거가 없을 때의 정해진 문구 + 빈 source_ids + 부족 사유 명시
    insufficient = {
        "status": "insufficient_context",
        "answer": NO_ANSWER,
        "source_ids": [],
        "missing_information": "정확한 과제 마감 날짜가 자료에 없습니다.",
    }
    # [사례 3: 허용되지 않은 출처 ID 반례] Context에 없는 가짜 ID 999를 인용 → 거절 대상!
    unknown = {**answered, "source_ids": [999]}
    return [
        {"name": "normal", "bundle": fixture_bundle(answered)},
        {"name": "insufficient", "bundle": fixture_bundle(insufficient)},
        {"name": "unknown_source", "bundle": fixture_bundle(unknown)},
    ]


def allowed_source_ids(included_docs):
    """입력: 실제 Context에 포함된 Document 목록 / 출력: set[int]."""
    # BEGIN D26-07-B01
    # [흐름 이해: 허용 출처 집합(provided_ids) 확정하기]
    # - 검색 후보 전체(documents)가 아니라, build_context()를 통과해 모델이 실제로 읽은
    #   'included_docs'에서만 citation_id를 뽑아야 합니다.
    # - set 컴프리헨션({... for ...})으로 반환하면 receive_bundle() 내부의 부분집합 검사
    #   (set(ids).issubset(provided_ids))와 바로 호환됩니다.
    return {doc.metadata["citation_id"] for doc in included_docs}
    # END D26-07-B01


def inspect_case(case, provided_ids):
    """검증 결과를 JSON으로 기록합니다. 원문 의미의 참/거짓은 자동 판정하지 않습니다."""
    # BEGIN D26-07-B02
    # [흐름 이해: 4단계 검문소(receive_bundle) 실행 후 승인/거절 리포트 기록]
    # - 성공 시: KnowledgeAnswer 객체가 반환됨 → model_dump()로 4필드 dict 변환
    #            outcome="accepted", error=None, human_review_required=True
    #            ※ 왜 True인가? 기계 검사(형식·ID)를 통과했어도 문장이 원문 사실과 맞는지
    #              사람이 한 번 더 대조(Grounding 확인)해야 하기 때문입니다!
    # - 실패 시: RagServiceError가 발생함 → 예외를 잡아 str(exc)로 오류 코드 기록
    #            outcome="rejected", result=None, human_review_required=False
    #            ※ 이미 규칙 위반으로 차단된 응답이므로 원문 대조 대상(result)이 없습니다.
    try:
        validated = receive_bundle(case["bundle"], provided_ids)
    except RagServiceError as exc:
        return {
            "case": case["name"],
            "outcome": "rejected",
            "error": str(exc),
            "result": None,
            "human_review_required": False,
        }

    return {
        "case": case["name"],
        "outcome": "accepted",
        "error": None,
        "result": validated.model_dump(),
        "human_review_required": True,
    }
    # END D26-07-B02


def run():
    # 1) 출석 예시 1건으로 Document → Context 및 실제 포함 문서(included_docs) 생성
    documents = hits_to_documents([example_hit()])
    context, included_docs = build_context(documents)

    # 2) [1단계 TODO] 실제 Context에 포함된 ID 집합 {201} 확보
    provided_ids = allowed_source_ids(included_docs)

    # 3) [2단계 TODO] 세 가지 고정 테스트 사례(normal, insufficient, unknown_source) 검증
    cases = common_cases()
    return {
        "source_mode": "validation_fixtures",
        "execution": execution_record("offline"),
        "context": context,
        "included_ids": sorted(provided_ids),
        "cases": [inspect_case(case, provided_ids) for case in cases],
        "grounding_review": "reports/review.md에서 숫자·조건·예외와 원문 위치를 직접 대조합니다.",
    }


def main():
    report = run()
    path = save_json(HERE, "validation_report.json", report)
    show_success("07 · 고정 입력 검증표 (모델·DB 미실행)", path)
    for row in report["cases"]:
        print(row["case"], row["outcome"], row["error"])
    print("accepted는 기계 검사를 통과했다는 뜻입니다. 원문 대조를 마쳐야 학습이 완료됩니다.")


if __name__ == "__main__":
    main()