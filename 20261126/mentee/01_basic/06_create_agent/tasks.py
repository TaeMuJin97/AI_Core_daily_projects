"""06 · create_agent + 실제 Tool 2개 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from coursekit.contracts import report_id_from


def question_for_agent(report_id: int) -> str:
    """내용 검색 + 인덱싱 상태를 모두 묻는 자연어 질문을 만듭니다."""
    # TODO D29-06-B-01
    # [흐름 이해: 두 Tool(rag_search, lookup_status)을 모두 유도하는 복합 질문 생성]
    # 1) report_id_from()으로 양의 정수 reports.report_id인지 검증합니다.
    # 2) 문서 근거 검색(rag_search) + 특정 보고서 인덱싱 상태 조회(lookup_status)가
    #    모두 필요한 자연어 질문을 반환합니다.
    rid = report_id_from(report_id)
    return (
        "RAG 근거 인용 정확도 향상과 관련된 보고서의 내용을 찾아 출처를 제시하고, "
        f"보고서 {rid}번의 인덱싱 상태도 알려줘."
    )


def make_agent():
    """create_agent + 등록 Tool 2개 + LLM Model + Tool Call 상한을 설정."""
    # TODO D29-06-B-02
    # [흐름 이해: 단일 Agent Harness에 Model · Tool 2개 · System Prompt · 호출 상한 연결]
    # 1) --check 실행 시 무거운 SDK/GPU 로딩을 피하기 위해 함수 내부에서 import합니다.
    # 2) LLM API 설정(require_llm_settings)과 CUDA GPU(require_cuda)를 사전 검증합니다.
    # 3) coursekit.agent.build_tools()로 실제 report_agent_lab 기반 2개 Tool
    #    (rag_search, lookup_status)을 등록합니다.
    # 4) ToolCallLimitMiddleware · ModelCallLimitMiddleware로 반복 폭주를 방지합니다.
    from langchain.agents import create_agent
    from langchain.agents.middleware import (
        ModelCallLimitMiddleware,
        ToolCallLimitMiddleware,
    )
    from langchain_openai import ChatOpenAI

    from coursekit.agent import SYSTEM_PROMPT, build_tools
    from coursekit.gpu import require_cuda
    from coursekit.settings import require_llm_settings

    cfg = require_llm_settings()
    require_cuda()

    model = ChatOpenAI(
        model=cfg.llm_model,
        timeout=45,
        max_retries=1,
    )

    tools = build_tools()  # [rag_search, lookup_status]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            ToolCallLimitMiddleware(
                run_limit=cfg.max_tool_calls,
                exit_behavior="error",
            ),
            ModelCallLimitMiddleware(
                run_limit=6,
                exit_behavior="error",
            ),
        ],
    )