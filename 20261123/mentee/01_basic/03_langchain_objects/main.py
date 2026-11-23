"""Day26 실습. 실행 위치와 관계없이 현재 역할 폴더의 지원 모듈을 사용합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent        # 현재 파일(main.py)이 위치한 폴더 (03_langchain_objects)
ROLE_ROOT = HERE.parents[1]                   # 두 단계 상위 폴더 (mentee 또는 mentor 루트)
sys.path.insert(0, str(ROLE_ROOT))            # Python 모듈 탐색 경로 맨 앞에 추가

from coursekit.io import save_json, show_success
from coursekit.data import example_hit, load_hits
from coursekit.reporting import execution_record

# -----------------------------------------------------------------------------
# 2. LangChain 4대 핵심 구성요소가 '입력(Input)'으로 받는 형태 (고정 제공)
#    → 아래 두 함수에서 이 4개 이름(Key)에 맞춰 '출력(Output)'과 '접근 방식(Access)'을 짝지어야 합니다.
# -----------------------------------------------------------------------------
COMPONENT_INPUTS = {
    "Document": "page_content와 metadata를 담아 생성",
    "Retriever": "query·category·candidate_k가 있는 dict",
    "Prompt": "question·context가 있는 dict",
    "Chat Model": "ChatPromptValue 또는 메시지 목록",
}


def component_outputs() -> dict[str, str]:
    """강의에서 다룬 네 구성요소의 출력 자료형을 대응시킵니다."""
    # BEGIN D26-03-B01
    # [흐름 이해: 앞 단계의 출력이 다음 단계의 입력과 맞물려야 파이프라인(|)이 돌아갑니다!]
    # 1) Document   : 검색된 청크 1건을 담는 데이터 객체 (page_content=본문, metadata=출처)
    # 2) Retriever  : 검색 요청 dict를 받아 조건에 맞는 문서 목록인 list[Document] 반환
    #                 ※ 주의: list[Document]를 Prompt에 바로 넣지 못하므로, 중간에 Context 문자열로 변환함!
    # 3) Prompt     : {"question": ..., "context": ...} dict를 받아 메시지 묶음인 ChatPromptValue 반환 (로컬 작업)
    # 4) Chat Model : ChatPromptValue를 받아 외부 LLM에 요청하고 응답 객체인 AIMessage 반환 (API 호출)
    #
    # ※ 주의: main()에서 COMPONENT_INPUTS의 Key로 조회하므로 Key 4개 철자가 정확히 일치해야 합니다.
    return {
        "Document": "Document (page_content와 metadata로 본문·출처 보관)",
        "Retriever": "list[Document]",
        "Prompt": "ChatPromptValue",
        "Chat Model": "AIMessage",
    }
    # END D26-03-B01


def access_kinds() -> dict[str, str]:
    """데이터를 읽는 경우와 invoke로 작업을 실행하는 경우를 구분합니다."""
    # BEGIN D26-03-B02
    # [흐름 이해: '보관함(data)'과 '실행기(invoke)' 구분하기]
    # - Document  : 값을 담아두고 속성(.page_content, .metadata)으로 꺼내 읽는 'data' 객체
    # - Retriever : 요청을 넣어 검색을 실행하는 Runnable → 'invoke'
    # - Prompt    : 변수를 채워 메시지를 조립하는 Runnable → 'invoke' (로컬 실행, API 비용 X)
    # - Chat Model: 메시지를 모델에 보내 답변을 받는 Runnable → 'invoke' (실제 LLM API 호출 지점)
    return {
        "Document": "data",
        "Retriever": "invoke",
        "Prompt": "invoke",
        "Chat Model": "invoke",
    }
    # END D26-03-B02


def main():
    # 1) 각 구성요소의 출력 자료형(outputs)과 접근 방식(access) 딕셔너리 생성
    outputs = component_outputs()
    access = access_kinds()

    # 2) COMPONENT_INPUTS를 순회하며 [구성요소명 / 입력 / 출력 / 접근 방식] 대응표 조립
    #    - execution: 실제 DB·LLM을 부르지 않는 개념 확인 실행(concept_review)임을 명시
    report = {
        "execution": execution_record("concept_review"),
        "components": [
            {
                "component": name,
                "input": value,
                "output": outputs[name],
                "access": access[name],
            }
            for name, value in COMPONENT_INPUTS.items()
        ],
        "observation": "입력·출력 대응표; Prompt·모델 invoke는 실행하지 않음",
    }

    # 3) 현재 실습 폴더 아래 outputs/object_contracts.json 으로 저장 후 성공 메시지 출력
    path = save_json(HERE, "object_contracts.json", report)
    show_success("03 기본필수", path)


if __name__ == "__main__":
    main()