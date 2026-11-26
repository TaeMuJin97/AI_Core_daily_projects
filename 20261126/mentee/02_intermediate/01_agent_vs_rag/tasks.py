"""01 · AI Agent vs 고정 RAG/Workflow · 응용 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def classify_request(question: str) -> str:
    """질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent. """
    # TODO D29-01-I-01: 질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    raise NotImplementedError('D29-01-I-01: 직접 구현하세요')

def plan_for_request(question: str) -> dict:
    """처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다."""
    # TODO D29-01-I-02: 처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    raise NotImplementedError('D29-01-I-02: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from validation_01 import needs_two_sources
