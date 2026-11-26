"""08 · FastAPI → Agent → Tool → 응답 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def default_question() -> str:
    """실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열."""
    # TODO D29-08-B-01: 실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열.
    # 힌트: API status·answer·출처 ID 검증을 분리하고 인증 미구현 범위를 명시하세요.
    raise NotImplementedError('D29-08-B-01: 직접 구현하세요')

def api_response(run: dict) -> dict:
    """성공/실패와 최종 답변·출처 검증을 API 계약으로 변환."""
    # TODO D29-08-B-02: 성공/실패와 최종 답변·출처 검증을 API 계약으로 변환.
    # 힌트: API status·answer·출처 ID 검증을 분리하고 인증 미구현 범위를 명시하세요.
    raise NotImplementedError('D29-08-B-02: 직접 구현하세요')

