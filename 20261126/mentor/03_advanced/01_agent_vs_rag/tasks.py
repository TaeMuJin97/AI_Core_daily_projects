"""01 · AI Agent vs 고정 RAG/Workflow · 심화 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def classify_request(question: str) -> str:
    """질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent. """
    # 해설 D29-01-A-01: 업무 질문에서 문서 근거 조회와 구조화 상태 조회를 구분합니다.
    # 검수 기준: 규칙 기반 라우팅을 LLM Agent의 자율 선택과 혼동하지 않습니다.
    q=question.lower()
    has_db=any(t in q for t in ('상태','인덱싱','revision','ready','pending'))
    has_doc=any(t in q for t in ('찾아','내용','설명','근거','검색'))
    if has_db and has_doc:return 'agent'
    if has_db:return 'db'
    return 'rag'

def plan_for_request(question: str) -> dict:
    """처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다."""
    # 해설 D29-01-A-02: 업무 질문에서 문서 근거 조회와 구조화 상태 조회를 구분합니다.
    # 검수 기준: 규칙 기반 라우팅을 LLM Agent의 자율 선택과 혼동하지 않습니다.
    mode=classify_request(question)
    tools={'rag':['rag_search'],'db':['lookup_status'],'agent':['rag_search','lookup_status']}[mode]
    return {'strategy':mode,'tools':tools,'decision':'고정 조건에 따른 실습용 계획; 실제 Agent 선택은 06에서 LLM 수행'}


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from policy_01 import needs_two_sources, validate_plan
