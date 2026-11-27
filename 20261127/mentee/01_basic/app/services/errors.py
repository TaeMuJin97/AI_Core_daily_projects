"""B-14/A-05: 원본 예외나 비밀번호를 HTTP 응답으로 반환하지 않는다."""
ERRORS = {
    'VALIDATION_ERROR': (422, '입력 형식과 범위를 확인하세요.'),
    'RUN_NOT_FOUND': (404, '현재 프로세스에 해당 실행 기록이 없습니다.'),
    'DB_UNAVAILABLE': (503, '기존 report_agent_lab 연결·스키마·권한을 확인하세요.'),
    'GPU_UNAVAILABLE': (503, 'CUDA 장치를 확인하세요. CPU 자동 전환은 하지 않습니다.'),
    'EMBEDDING_UNAVAILABLE': (503, 'E5 로딩·추론 또는 유효 벡터 준비 상태를 확인하세요.'),
    'RERANKER_UNAVAILABLE': (503, 'Cross-Encoder 로딩·추론·VRAM을 확인하세요.'),
    'LLM_UNAVAILABLE': (503, 'LLM 키·모델·요청 제한·서비스 상태를 확인하세요.'),
    'LLM_TIMEOUT': (504, 'LLM 응답 시간이 초과되었습니다.'),
    'TOOL_CONTRACT_ERROR': (500, 'Tool 출력 또는 실행 기록 계약 위반입니다.'),
    'OUTPUT_CONTRACT_ERROR': (500, '모델 출력 형식 또는 출처 계약 위반입니다.'),
    'CONFIG_INVALID': (503, '환경 설정 범위를 확인하세요.'),
    'EXECUTION_LIMIT': (503, '서버 실행 예산을 초과했습니다.'),
    'NOT_IMPLEMENTED': (500, 'TODO 구현을 완료하세요.'),
}
class ServiceError(Exception):
    def __init__(self, code, reason=None, retryable=False):
        self.code = code
        self.http_status, self.message = ERRORS[code]
        self.reason = reason  # 서버가 정의한 안전한 분류값만 사용
        self.retryable = retryable
        super().__init__(code)
    def envelope(self):
        details = {'reason': self.reason, 'retryable': self.retryable} if self.reason else {}
        return {'error': {'code': self.code, 'message': self.message, 'details': details}}


def llm_error(exc):
    if isinstance(exc, ServiceError):
        return exc
    # 원본 문자열을 읽거나 노출할 필요 없이 SDK 예외 종류 및 상태코드로 분류.
    name = type(exc).__name__
    code = getattr(exc, 'status_code', None)
    if name in ('APITimeoutError','TimeoutError','ReadTimeout','ConnectTimeout'):
        return ServiceError('LLM_TIMEOUT', 'timeout', True)
    if code in (401,403) or name == 'AuthenticationError':
        return ServiceError('LLM_UNAVAILABLE', 'authentication')
    if code == 429 or name == 'RateLimitError':
        return ServiceError('LLM_UNAVAILABLE', 'rate_limit', True)
    if isinstance(code,int) and code >= 500:
        return ServiceError('LLM_UNAVAILABLE', 'upstream_5xx', True)
    return ServiceError('LLM_UNAVAILABLE', 'provider_error')
