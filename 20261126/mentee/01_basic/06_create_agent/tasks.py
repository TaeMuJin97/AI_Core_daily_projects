"""06 · create_agent + 실제 Tool 2개 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def question_for_agent(report_id: int) -> str:
    """내용 검색 + 인덱싱 상태를 모두 묻는 자연어 질문을 만듭니다."""
    # TODO D29-06-B-01: 내용 검색 + 인덱싱 상태를 모두 묻는 자연어 질문을 만듭니다.
    # 힌트: create_agent에 두 Tool을 등록하고 AIMessage와 ToolMessage를 구별하세요.
    raise NotImplementedError('D29-06-B-01: 직접 구현하세요')

def make_agent():
    """create_agent + 등록 Tool 2개 + LLM Model + Tool Call 상한을 설정."""
    # TODO D29-06-B-02: create_agent + 등록 Tool 2개 + LLM Model + Tool Call 상한을 설정.
    # 힌트: create_agent에 두 Tool을 등록하고 AIMessage와 ToolMessage를 구별하세요.
    raise NotImplementedError('D29-06-B-02: 직접 구현하세요')

