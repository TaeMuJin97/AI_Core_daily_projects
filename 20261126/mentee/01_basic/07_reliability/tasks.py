"""07 · Tool 실패·권한·반복 상한 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from coursekit.contracts import report_id_from


def validate_report_id(value) -> int:
    """invalid args는 DB 쿼리 전에 차단합니다."""
    # TODO D29-07-B-01
    # [흐름 이해: 잘못된 report_id가 PostgreSQL 쿼리로 전달되기 전에 즉시 차단]
    # 1) coursekit.contracts.report_id_from()을 사용해:
    #    - 63, '63' 같은 유효한 양의 정수는 int(63)으로 반환합니다.
    #    - -1, 0, bool(True/False), 소수, 선행 0('063'), SQL 문자열 등은
    #      모두 ValueError를 발생시켜 DB 조회 전에 차단합니다.
    return report_id_from(value)


def classify_error(exc: Exception) -> dict:
    """사용자 입력 오류와 연결 오류를 구분. 비밀정보·SQL 원문 로그 노출 금지."""
    # TODO D29-07-B-02
    # [흐름 이해: 예외를 원인별 error_code로 분류하고, 원문(비밀번호·SQL·키)은 절대 반환하지 않음]
    # - 주의 1: 어떤 예외도 'not_found' 또는 'insufficient_context'(no-answer)로 위장하지 않습니다.
    # - 주의 2: str(exc)에는 DATABASE_URL, password, SQL 원문, API Key가 포함될 수 있으므로
    #           반환 dict에 원문 예외 문자열을 그대로 넣지 않고 정해진 안전 문구만 사용합니다.
    if not isinstance(exc, Exception):
        raise TypeError("exc는 Exception 인스턴스여야 합니다.")

    exc_type = type(exc).__name__
    exc_module = (type(exc).__module__ or "").lower()
    exc_type_lower = exc_type.lower()
    raw_lower = str(exc).lower()

    # 1) 권한·허용 범위 위반 (예: ALLOWED_CATEGORIES 외 접근)
    if isinstance(exc, PermissionError):
        return {
            "status": "error",
            "error_code": "forbidden",
            "category": "authorization",
            "http_status": 403,
            "retryable": False,
            "is_no_answer": False,
            "safe_message": "허용되지 않은 리소스 또는 카테고리 접근 요청입니다.",
        }

    # 2) 사용자 입력·Schema 검증 오류 (예: report_id=-1, Pydantic ValidationError)
    if isinstance(exc, (ValueError, TypeError)) or "validation" in exc_type_lower:
        return {
            "status": "error",
            "error_code": "invalid_input",
            "category": "client_input",
            "http_status": 422,
            "retryable": False,
            "is_no_answer": False,
            "safe_message": "도구 입력값 형식이 올바르지 않아 실행 전에 차단되었습니다.",
        }

    # 3) Tool/Model 반복 호출 상한 초과 (ToolCallLimitMiddleware · ModelCallLimitMiddleware · recursion_limit)
    if (
        "limit" in exc_type_lower
        or "recursion" in exc_type_lower
        or "run_limit" in raw_lower
        or "recursion limit" in raw_lower
    ):
        return {
            "status": "error",
            "error_code": "loop_limit_exceeded",
            "category": "execution_policy",
            "http_status": 429,
            "retryable": False,
            "is_no_answer": False,
            "safe_message": "Agent 도구 또는 모델 호출 상한을 초과하여 실행을 중단했습니다.",
        }

    # 4) 요청·쿼리 타임아웃
    if isinstance(exc, TimeoutError) or "timeout" in exc_type_lower:
        return {
            "status": "error",
            "error_code": "timeout_error",
            "category": "infrastructure",
            "http_status": 504,
            "retryable": True,
            "is_no_answer": False,
            "safe_message": "외부 서비스 또는 데이터베이스 응답 시간이 초과되었습니다.",
        }

    # 5) DB 연결·인증·트랜잭션 장애 (psycopg / sqlalchemy / 네트워크 연결 오류)
    if (
        isinstance(exc, ConnectionError)
        or "psycopg" in exc_module
        or "sqlalchemy" in exc_module
        or any(tok in exc_type_lower for tok in ("operational", "database", "interface", "connection"))
    ):
        return {
            "status": "error",
            "error_code": "db_connection_error",
            "category": "database",
            "http_status": 503,
            "retryable": True,
            "is_no_answer": False,
            "safe_message": "데이터베이스 연결 또는 조회 중 시스템 오류가 발생했습니다.",
        }

    # 6) GPU / CUDA 오류 (예: CUDA OOM, cuda:0 미사용)
    if (
        "outofmemory" in exc_type_lower
        or "cuda" in raw_lower
        or "out of memory" in raw_lower
    ):
        return {
            "status": "error",
            "error_code": "gpu_runtime_error",
            "category": "gpu",
            "http_status": 503,
            "retryable": False,
            "is_no_answer": False,
            "safe_message": "GPU(CUDA) 추론 환경 오류로 요청을 완료할 수 없습니다.",
        }

    # 7) 외부 LLM API 인증·호출 장애 (OpenAI 401/429/5xx 등)
    if "openai" in exc_module or "authentication" in exc_type_lower or "ratelimit" in exc_type_lower:
        is_auth = "authentication" in exc_type_lower or "401" in raw_lower
        return {
            "status": "error",
            "error_code": "llm_auth_error" if is_auth else "llm_provider_error",
            "category": "llm_provider",
            "http_status": 502,
            "retryable": not is_auth,
            "is_no_answer": False,
            "safe_message": "LLM API 인증 또는 외부 모델 호출 중 오류가 발생했습니다.",
        }

    # 8) 기타 미분류 서버 오류 (Fail Closed: 정상 응답이나 정보 부족으로 변환 금지)
    return {
        "status": "error",
        "error_code": "internal_service_error",
        "category": "system",
        "http_status": 500,
        "retryable": False,
        "is_no_answer": False,
        "safe_message": "내부 서비스 처리 중 예상하지 못한 오류가 발생했습니다.",
    }