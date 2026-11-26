"""경계값·오류/권한 정책: Advanced · Day29."""

def format_evidence(result: dict) -> dict:
    """RAG 답변·실제 Context 출처·상태를 구분해 결과로 반환."""
    # TODO D29-04-A-03: RAG 답변·실제 Context 출처·상태를 구분해 결과로 반환.
    # 힌트: 실제 query/category 검증 후 coursekit.rag의 live 연결을 호출하세요.
    raise NotImplementedError('D29-04-A-03: 직접 구현하세요')

def validate_evidence(result: dict) -> bool:
    """선택된 Context 내 출처만 인정하고 No-answer 출처를 거절합니다."""
    # TODO D29-04-A-04: 선택된 Context 내 출처만 인정하고 No-answer 출처를 거절합니다.
    # 힌트: 실제 query/category 검증 후 coursekit.rag의 live 연결을 호출하세요.
    raise NotImplementedError('D29-04-A-04: 직접 구현하세요')

