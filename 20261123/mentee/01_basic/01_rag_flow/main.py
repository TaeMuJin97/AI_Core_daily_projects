"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent        # 현재 파일(main.py)이 있는 폴더 (01_rag_flow)
ROLE_ROOT = HERE.parents[1]                   # 두 단계 상위 폴더 (mentee 또는 mentor 루트)
sys.path.insert(0, str(ROLE_ROOT))            # Python 모듈 탐색 경로 맨 앞에 추가

from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record

# -----------------------------------------------------------------------------
# 2. RAG 5단계별 입력·출력 명세 (순서가 섞인 dict로 제공됨)
#    → stage_order()가 반환하는 이름 목록으로 이 dict에서 정확한 순서대로 꺼내 씁니다.
# -----------------------------------------------------------------------------
STAGE_CARDS = {
    "Generator": {"input": "모델 입력", "output": "생성된 답변"},
    "Prompt": {"input": "규칙·질문·Context", "output": "모델이 읽을 메시지"},
    "Retriever": {"input": "질문·검색 조건", "output": "관련 청크 후보"},
    "Validator · Source 연결": {"input": "생성 결과·허용 ID", "output": "검증 결과·원문 위치"},
    "Context Builder": {"input": "후보 목록", "output": "선택한 근거·포함 ID"},
}


def stage_order() -> list[str]:
    """STAGE_CARDS의 이름 다섯 개를 처리 순서대로 반환합니다."""
    # BEGIN D26-01-B01
    # [RAG 서비스 내부 5단계 처리 흐름]
    # 1) Retriever              : 질문·검색 조건(Category, k)으로 관련 청크 후보를 찾음
    # 2) Context Builder        : 후보 중 실제 모델에 넣을 본문을 고르고 허용 ID(included_ids)를 별도 보관
    # 3) Prompt                 : 고정 규칙(system) + 질문·Context(human)를 합쳐 모델 입력 메시지 작성
    # 4) Generator              : 준비된 메시지로 LLM을 호출해 답변 초안 생성
    # 5) Validator · Source 연결 : 생성 결과의 형식·출처 ID(허용 ID 대조)를 검사하고 실제 원문 위치 연결
    # ※ 주의: STAGE_CARDS의 Key 문자열(가운뎃점 '·' 및 띄어쓰기 포함)과 정확히 일치해야 KeyError가 나지 않음
    return [
        "Retriever",
        "Context Builder",
        "Prompt",
        "Generator",
        "Validator · Source 연결",
    ]
    # END D26-01-B01


def evidence_note(hit: dict) -> dict:
    """출석 문서와 사람이 읽은 판단을 함께 기록합니다. 모델 호출 결과가 아닙니다."""
    # BEGIN D26-01-B02
    # [완료 기준 체크]
    # 1) 입력 Hit의 본문(body)·ID(citation_id, doc_id)·버전(source_version)·원문 위치(source_locator)를
    #    손실 없이 그대로 보존해야 함 → 추후 답변의 출처를 원문까지 역추적하는 RAG의 핵심 계약
    # 2) 15분 질문 판단: 원문의 "15분까지 지각 / 15분 초과 결석" 경계를 정확히 해석해 '지각'으로 기록
    # 3) 예외 조건 보존: "단, 사전 승인을 받은 경우에는 운영실에 확인" 예외를 누락하지 않고 함께 남김
    return {
        "question": "15분 늦으면 어떻게 기록되나요?",
        "citation_id": hit["citation_id"],        # 답변 source_ids에서 가리킬 정수 출처 ID (예시: 201)
        "doc_id": hit["doc_id"],                  # 어떤 문서인지 식별하는 문서 ID (예시: DOC-ATTEND)
        "source_version": hit["source_version"],  # 최신 공개 버전 확인용 (예시: v2, 과거 v1과 구분)
        "source_locator": hit["source_locator"],  # 실제 원문 파일·섹션 위치 (예시: attendance_v2.md#sec-1)
        "body": hit["body"],                      # 검색된 출석 규정 청크 원문 그대로 보존
        "judgment": "지각 (수업 시작 후 15분까지 입실하면 지각으로 기록, 15분 초과 시 결석)",
        "exception": "단, 사전 승인을 받은 경우에는 운영실에 확인합니다.",
    }
    # END D26-01-B02


def main():
    # 1) 올바른 RAG 5단계 순서 리스트 획득
    order = stage_order()

    # 2) 최종 결과 리포트 구성
    #    - execution: 실제 DB/LLM 호출이 아닌 'concept_review(개념 확인)' 실행임을 명시
    #    - stages   : order 순서대로 STAGE_CARDS에서 input/output을 꺼내(언패킹 **) 단계별 카드 배열 생성
    #    - case     : 예시 출석 Hit(example_hit())의 출처·본문과 사람이 판독한 15분 판단·예외 기록
    report = {
        "execution": execution_record("concept_review"),
        "stages": [{"stage": name, **STAGE_CARDS[name]} for name in order],
        "case": evidence_note(example_hit()),
        "observation": "사람이 강의 원문을 읽고 작성한 역할·근거 확인표",
    }

    # 3) 현재 실습 폴더 아래 outputs/rag_flow.json 으로 저장 후 성공 메시지 출력
    path = save_json(HERE, "rag_flow.json", report)
    show_success("01 Basic", path)


if __name__ == "__main__":
    main()