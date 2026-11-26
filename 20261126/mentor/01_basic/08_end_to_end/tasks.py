"""08 · FastAPI → Agent → Tool → 응답 · 기본필수 · 강사용 정답.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def default_question() -> str:
    """실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열."""
    # 해설 D29-08-B-01: FastAPI는 사용자의 입력을 검증해 Agent에 전달하고 최종 결과를 반환합니다.
    # 검수 기준: 인용 ID가 실제 Tool 근거 집합 밖이면 성공 응답으로 위장하지 않습니다.
    from coursekit.live import demo_question
    return demo_question()

def api_response(run: dict) -> dict:
    """성공/실패와 최종 답변·출처 검증을 API 계약으로 변환."""
    # 해설 D29-08-B-02: FastAPI는 사용자의 입력을 검증해 Agent에 전달하고 최종 결과를 반환합니다.
    # 검수 기준: 인용 ID가 실제 Tool 근거 집합 밖이면 성공 응답으로 위장하지 않습니다.
    if run.get('status')!='completed':raise RuntimeError('Agent did not complete')
    if run.get('citation_ids_valid') is not True:
        raise RuntimeError('UNVERIFIED_CITATION: Agent가 제공되지 않은 출처 ID를 인용했습니다.')
    return {'status':'completed','answer':run['answer'],
            'tool_trace':run['tool_trace'],
            'citation_ids_valid':run['citation_ids_valid'],
            'verified_evidence_ids':run['verified_evidence_ids']}

