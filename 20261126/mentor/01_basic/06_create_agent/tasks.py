"""06 · create_agent + 실제 Tool 2개 · 기본필수 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def question_for_agent(report_id: int) -> str:
    """내용 검색 + 인덱싱 상태를 모두 묻는 자연어 질문을 만듭니다."""
    # 해설 D29-06-B-01: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    from coursekit.contracts import report_id_from
    rid=report_id_from(report_id)
    return f"RAG 근거 인용 정확도 향상과 관련된 보고서 내용을 설명하고, {rid}번 보고서의 인덱싱 상태도 알려줘."

def make_agent():
    """create_agent + 등록 Tool 2개 + LLM Model + Tool Call 상한을 설정."""
    # 해설 D29-06-B-02: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    from coursekit.agent import build_tools,SYSTEM_PROMPT
    from coursekit.settings import require_llm_settings,settings
    from langchain.agents import create_agent
    from langchain.agents.middleware import ToolCallLimitMiddleware,ModelCallLimitMiddleware
    from langchain_openai import ChatOpenAI
    require_llm_settings()
    return create_agent(model=ChatOpenAI(model=settings().llm_model,timeout=45,max_retries=1),
        tools=build_tools(),system_prompt=SYSTEM_PROMPT,
        middleware=[ToolCallLimitMiddleware(run_limit=4,exit_behavior='error'),
                    ModelCallLimitMiddleware(run_limit=6,exit_behavior='error')])

