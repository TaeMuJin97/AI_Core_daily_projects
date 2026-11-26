"""01 · AI Agent vs 고정 RAG/Workflow · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
import re

# 문서(report_read_view) 본문 검색·근거 설명 의도를 나타내는 키워드
_RAG_KEYWORDS = (
    "내용",
    "설명",
    "찾아",
    "검색",
    "근거",
    "규정",
    "요약",
    "문서",
    "안내",
    "원문",
    "인용",
    "정확도",
    "rag",
    "policy",
)

# 운영 DB(reports) 상태·인덱싱·특정 ID 조회 의도를 나타내는 키워드
_DB_STATUS_KEYWORDS = (
    "인덱싱",
    "상태",
    "index_status",
    "ready",
    "pending",
    "failed",
    "revision",
    "제출 상태",
    "제출됐",
    "여부",
    "report_id",
)

# "보고서 63번", "63번 보고서", "id 63" 등 특정 레코드 ID 지칭 패턴
_REPORT_ID_PATTERN = re.compile(r"(?:보고서\s*\d+|\d+\s*번|report_id\s*[:=]?\s*\d+)", re.IGNORECASE)


def classify_request(question: str) -> str:
    """질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent."""
    # TODO D29-01-B-01
    # [흐름 이해: 데이터 출처(문서 원문 vs DB 상태)에 따라 처리 전략 분류]
    # 1) 빈 문자열 등 잘못된 입력은 조용히 넘기지 않고 ValueError로 차단합니다.
    # 2) 문서/규정/내용 탐색 의도(needs_rag)와 DB 상태/인덱싱 조회 의도(needs_db)를 각각 판별합니다.
    # 3) 둘 다 필요하면 'agent', DB 상태만 필요하면 'db', 그 외 문서 질문은 'rag'를 반환합니다.
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question은 비어 있지 않은 문자열이어야 합니다.")

    normalized = question.strip().lower()

    needs_rag = any(keyword in normalized for keyword in _RAG_KEYWORDS)
    needs_db = any(keyword in normalized for keyword in _DB_STATUS_KEYWORDS)

    # 상태 키워드 없이 특정 번호만 언급된 경우도 DB 조회 단서로 보되,
    # "63번 보고서 내용을 요약해줘"처럼 명백히 내용 요청만 있을 때는 RAG와 구분합니다.
    if not needs_db and _REPORT_ID_PATTERN.search(normalized) and not needs_rag:
        needs_db = True

    if needs_rag and needs_db:
        return "agent"
    if needs_db:
        return "db"
    return "rag"


def plan_for_request(question: str) -> dict:
    """처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다."""
    # TODO D29-01-B-02
    # [흐름 이해: 분류된 strategy에 맞는 Tool 목록을 명시적 dict 계약으로 반환]
    # - 'rag'   -> ['rag_search']                (문서 검색으로 충분)
    # - 'db'    -> ['lookup_status']             (기존 DB SELECT 상태 조회)
    # - 'agent' -> ['rag_search', 'lookup_status'] (문서 검색 + DB 상태 복합 처리)
    # 주의: 이 함수는 규칙 기반 사전 계획(Rule-based Plan)이며,
    #       실제 LLM이 동적으로 도구를 선택하는 Agent 판단과는 다릅니다.
    strategy = classify_request(question)

    tool_map = {
        "rag": (
            ["rag_search"],
            "문서/규정 본문 근거가 필요한 요청이므로 고정 RAG 검색 Tool로 처리할 수 있습니다.",
        ),
        "db": (
            ["lookup_status"],
            "특정 report_id의 현재 인덱싱 상태 조회가 필요하므로 PostgreSQL 읽기 전용 Tool이 필요합니다.",
        ),
        "agent": (
            ["rag_search", "lookup_status"],
            "문서 근거 검색(report_read_view)과 DB 상태 조회(reports.index_status)가 모두 필요한 복합 요청입니다.",
        ),
    }

    tools, reason = tool_map[strategy]

    return {
        "question": question.strip(),
        "strategy": strategy,
        "tools": tools,
        "is_llm_agent_decision": False,
        "reason": reason,
    }