"""공통 실행 도우미. 업무 구현 정답을 포함하지 않는다."""
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'http://127.0.0.1:8000'


def paid_opt_in():
    """비용 동의가 없으면 DB/모델 준비 전 종료한다."""
    p = argparse.ArgumentParser(description='실제 유료 LLM 검증')
    p.add_argument('--allow-paid-llm', action='store_true')
    args = p.parse_args()
    if not args.allow_paid_llm:
        p.error('유료 호출은 --allow-paid-llm을 명시한 경우에만 실행합니다.')


def report_ids():
    """실제 값은 .env에서 읽되 기존 환경변수가 우선한다."""
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env', override=False)
    try:
        rid = int(os.environ['DAY30_REPORT_ID'])
        missing = int(os.environ['DAY30_MISSING_ID'])
    except (KeyError, ValueError):
        raise SystemExit('.env의 DAY30_REPORT_ID / DAY30_MISSING_ID를 실제 양의 정수로 설정하세요.') from None
    assert 0 < rid <= 9223372036854775807 and 0 < missing <= 9223372036854775807 and rid != missing, '테스트 ID 범위/중복 오류'
    return rid, missing


def check_openapi():
    from app.main import app
    paths = set(app.openapi()['paths'])
    print('OpenAPI:', sorted(paths))
    assert {'/health', '/api/v1/agent/ask'} <= paths


def client():
    import httpx
    # localhost 직접 접속. 유료 요청도 있을 수 있어 자동 재시도하지 않는다.
    return httpx.Client(base_url=BASE_URL, timeout=300, trust_env=False)


def check_response(response, expected_status, expected_error=None):
    print('HTTP', response.status_code, response.request.method, response.request.url.path)
    data = response.json()
    print(data)  # 로컬 확인 전용. 보고서 원문/답변은 외부에 공유하지 않는다.
    assert response.status_code == expected_status, '예상 HTTP 상태와 다릅니다.'
    if expected_error is not None:
        assert data['error']['code'] == expected_error
    return data


def check_ready_http(c):
    data = check_response(c.get('/health'), 200)
    assert data['db'] == 'ready' and data['database'] == 'report_agent_lab'
    assert data['eligible_vectors'] > 0 and data['gpu'] == 'cuda:0'
    assert data['llm'] == 'configured' and data['llm_live_verified'] is False
    check_response(c.post('/api/v1/agent/ask', json={'question': ' '}), 422, 'VALIDATION_ERROR')


def check_completed(data, required_tools):
    assert data['status'] == 'completed', '전체 업무가 완료되지 않았습니다.'
    assert data['validation']['citations_match_context'] is True
    assert data['validation']['required_tools_observed'] is True
    found = {item['tool'] for item in data['tool_trace'] if item['status'] == 'found'}
    assert required_tools <= found, '필요한 실제 Tool 결과가 없습니다.'
