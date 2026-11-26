"""용도별 추가 검증: Intermediate · Day29."""

def format_evidence(result: dict) -> dict:
    """RAG 답변·실제 Context 출처·상태를 구분해 결과로 반환."""
    # 해설 D29-04-I-03: 실제 CUDA E5 query: 인코딩으로 11/20의 overview Vector를 검색합니다.
    # 검수 기준: CUDA CrossEncoder/LLM과 출처 ID 검증의 책임을 분리합니다.
    return {'status':result['status'],'answer':result['answer'],
            'source_ids':[x['source_id'] for x in result['sources']]}

