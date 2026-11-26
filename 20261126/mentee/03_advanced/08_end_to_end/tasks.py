"""08 · FastAPI → Agent → Tool → 응답 · 심화 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def default_question() -> str:
    """실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열."""
    # TODO D29-08-A-01: 실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열.
    # 힌트: API status·answer·출처 ID 검증을 분리하고 인증 미구현 범위를 명시하세요.
    raise NotImplementedError('D29-08-A-01: 직접 구현하세요')

def api_response(run: dict) -> dict:
    """성공/실패와 최종 답변·출처 검증을 API 계약으로 변환."""
    # TODO D29-08-A-02: 성공/실패와 최종 답변·출처 검증을 API 계약으로 변환.
    # 힌트: API status·answer·출처 ID 검증을 분리하고 인증 미구현 범위를 명시하세요.
    raise NotImplementedError('D29-08-A-02: 직접 구현하세요')

def make_api():
    """FastAPI에 POST /api/agent/ask 를 등록합니다. 로컬 교육용·인증 미구현."""
    # TODO D29-08-A-03: FastAPI에 POST /api/agent/ask 를 등록합니다. 로컬 교육용·인증 미구현.
    # 힌트: API status·answer·출처 ID 검증을 분리하고 인증 미구현 범위를 명시하세요.
    raise NotImplementedError('D29-08-A-03: 직접 구현하세요')


# 추가 구현: 같은 프로젝트의 별도 책임 모듈
from policy_08 import audit_response
