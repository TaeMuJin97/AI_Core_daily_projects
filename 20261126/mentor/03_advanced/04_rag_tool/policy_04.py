"""경계값·오류/권한 정책: Advanced · Day29."""

def format_evidence(result: dict) -> dict:
    """RAG 답변·실제 Context 출처·상태를 구분해 결과로 반환."""
    # 해설 D29-04-A-03: 실제 CUDA E5 query: 인코딩으로 11/20의 overview Vector를 검색합니다.
    # 검수 기준: CUDA CrossEncoder/LLM과 출처 ID 검증의 책임을 분리합니다.
    return {'status':result['status'],'answer':result['answer'],
            'source_ids':[x['source_id'] for x in result['sources']]}

def validate_evidence(result: dict) -> bool:
    """선택된 Context 내 출처만 인정하고 No-answer 출처를 거절합니다."""
    # 해설 D29-04-A-04: 실제 CUDA E5 query: 인코딩으로 11/20의 overview Vector를 검색합니다.
    # 검수 기준: CUDA CrossEncoder/LLM과 출처 ID 검증의 책임을 분리합니다.
    from coursekit.contracts import validate_source_contract
    verified={f"RPT-{rid}" for rid in result['retrieval']['included_ids']}
    return validate_source_contract(result,verified)

