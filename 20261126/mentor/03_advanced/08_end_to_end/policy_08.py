"""경계값·오류/권한 정책: Advanced · Day29."""

def audit_response(raw: dict) -> dict:
    """검증된 출처만 기록하고 성공으로 위장된 오류는 거절합니다."""
    # 해설 D29-08-A-04: FastAPI는 사용자의 입력을 검증해 Agent에 전달하고 최종 결과를 반환합니다.
    # 검수 기준: 인용 ID가 실제 Tool 근거 집합 밖이면 성공 응답으로 위장하지 않습니다.
    if raw.get('status')!='completed':raise ValueError('agent incomplete')
    if raw.get('citation_ids_valid') is not True:raise ValueError('invalid citations')
    return {'status':'verified','tools':len(raw.get('tool_trace',[]))}

