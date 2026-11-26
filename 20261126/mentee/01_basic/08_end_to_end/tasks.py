"""08 · FastAPI → Agent → Tool → 응답 · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from coursekit.contracts import SOURCE_ID_PATTERN

_FAILED_TOOL_STATUSES = frozenset({"error", "db_error", "timeout_error", "auth_error"})


def default_question() -> str:
    """실제 보고서 검색 + 63번 인덱싱 상태를 묻는 요청 문자열."""
    # TODO D29-08-B-01
    # [흐름 이해: rag_search(문서 내용·출처)와 lookup_status(63번 인덱싱 상태)를
    #  함께 검증할 수 있는 기본 복합 요청 문자열을 반환합니다.]
    return (
        "RAG 근거 인용 정확도 향상과 관련된 보고서의 내용을 찾아 출처를 제시하고, "
        "보고서 63번의 인덱싱 상태도 알려줘."
    )


def api_response(run: dict) -> dict:
    """성공/실패와 최종 답변·출처 검증을 API 계약으로 변환."""
    # TODO D29-08-B-02
    # [흐름 이해: run_agent() 실행 결과를 서버 측에서 재검증한 뒤 FastAPI JSON 계약으로 변환]
    # 1) 실행 상태(status == 'completed')와 최종 텍스트(answer)가 비어 있지 않은지 확인합니다.
    #    실패 시 RuntimeError를 발생시켜 starter.py가 HTTP 502로 차단하도록 합니다.
    # 2) Tool 실행 Trace에 명시적 시스템 오류 상태(error, db_error 등)가 섞여 있으면 Fail Closed로 중단합니다.
    # 3) 출처 ID 검증:
    #    - 최종 답변에서 추출한 RPT-번호(cited_source_ids)가 실제 ToolMessage의
    #      verified_evidence_ids 부분집합인지 확인합니다.
    #    - 미검증 RPT-번호를 인용했거나 citation_ids_valid=False이면 RuntimeError(HTTP 502)로 차단합니다.
    # 4) 출처 ID 일치는 Claim Faithfulness 자동 보증이 아니며, 사용자 인증·RBAC 미구현(로컬 전용)임을 명시합니다.
    if not isinstance(run, dict):
        raise RuntimeError("Agent 실행 결과는 dict 형식이어야 합니다.")

    if run.get("status") != "completed":
        raise RuntimeError(f"Agent 실행이 정상 완료되지 않았습니다: {run.get('status')!r}")

    answer = run.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Agent 최종 답변(answer)이 비어 있습니다.")
    clean_answer = answer.strip()

    # Tool Trace 중 시스템 오류가 있었다면 정상 응답으로 위장하지 않고 차단
    tool_trace = run.get("tool_trace", [])
    if not isinstance(tool_trace, list):
        raise RuntimeError("tool_trace는 list 형식이어야 합니다.")
    for item in tool_trace:
        if isinstance(item, dict) and item.get("status") in _FAILED_TOOL_STATUSES:
            raise RuntimeError(f"Tool 실행 오류가 감지되었습니다: {item.get('status')!r}")

    # 최종 답변의 RPT-번호와 Tool이 실제로 제공한 verified_evidence_ids 대조
    cited_from_text = set(SOURCE_ID_PATTERN.findall(clean_answer))
    cited_from_run = set(run.get("cited_source_ids") or [])
    cited_ids = sorted(cited_from_text | cited_from_run)

    has_verified = "verified_evidence_ids" in run
    verified_ids = sorted(set(run.get("verified_evidence_ids") or []))
    explicit_valid = run.get("citation_ids_valid")

    if explicit_valid is False:
        raise RuntimeError("검증되지 않은 RPT-번호 출처가 인용되어 응답을 차단했습니다.")
    if has_verified and not set(cited_ids).issubset(set(verified_ids)):
        raise RuntimeError("최종 답변에 Tool 근거에 없는 RPT-번호 출처가 포함되어 있습니다.")
    if not has_verified and explicit_valid is None and cited_ids:
        raise RuntimeError("검증된 출처 목록 없이 RPT-번호 인용이 포함되어 있습니다.")

    return {
        "status": "ok",
        "answer": clean_answer,
        "citation_ids_valid": True,
        "cited_source_ids": cited_ids,
        "verified_evidence_ids": verified_ids,
        "faithfulness_checked": False,
        "tool_call_summary": run.get("tool_call_summary", {}),
        "tool_trace": tool_trace,
        "auth_scope": {
            "deployment_scope": "local_only_127_0_0_1",
            "user_authentication": False,
            "rbac_enabled": False,
            "note": "사용자 인증·RBAC 미구현 교육용 읽기 전용 API입니다. 외부 서비스 배포 금지.",
        },
    }