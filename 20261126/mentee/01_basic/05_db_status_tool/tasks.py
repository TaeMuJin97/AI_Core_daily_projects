"""05 · PostgreSQL Read-only lookup_status · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""
from coursekit.contracts import report_id_from

_VALID_INDEX_STATUSES = frozenset({"pending", "ready", "failed"})


def parse_report_id(value) -> int:
    """task_id가 아니라 reports.report_id. 임의로 문자열을 SQL에 붙이지 않습니다."""
    # TODO D29-05-B-01
    # [흐름 이해: 사용자/모델이 넘긴 값을 안전한 양의 정수 report_id로 변환]
    # 1) coursekit.contracts.report_id_from()을 사용해:
    #    - '63' 같은 숫자 문자열은 정수 63으로 변환합니다.
    #    - bool(True/False), 소수(63.5), 0/음수, 선행 0('063'), SQL 조각('63 OR 1=1')은
    #      모두 ValueError로 차단합니다.
    # 2) 반환된 정수만 Parameterized SQL(:rid)의 바인딩 값으로 전달됩니다.
    return report_id_from(value)


def status_view(raw: dict) -> dict:
    """pending/ready/failed와 실제 벡터 정합성을 구분해 표시."""
    # TODO D29-05-B-02
    # [흐름 이해: DB 상태(index_status)와 벡터 최신성(vector_fresh)을 분리해 읽기 좋게 정리]
    # 1) status가 'not_found' / 'not_found_or_forbidden'이면 정상 미조회 결과로 정리합니다.
    # 2) status가 'ok'가 아닌 알 수 없는 상태라면 서비스 오류로 보고 RuntimeError를 발생시킵니다.
    # 3) status == 'ok'이면:
    #    - index_status가 실제 DB 계약('pending', 'ready', 'failed')인지 검사합니다.
    #    - vector_fresh는 revision 일치 + E5 모델 일치 + overview SHA-256 일치 검사 결과입니다.
    #    - index_status == 'ready'이면서 vector_fresh == True일 때만 실제 RAG 검색 가능(searchable)합니다.
    if not isinstance(raw, dict):
        raise TypeError("raw는 fetch_report_status()가 반환한 dict여야 합니다.")

    status = raw.get("status")
    report_id = raw.get("report_id")

    if status in {"not_found", "not_found_or_forbidden"}:
        return {
            "status": status,
            "report_id": report_id,
            "index_status": None,
            "vector_fresh": False,
            "searchable": False,
            "summary": f"보고서 {report_id}번을 조회할 수 없습니다 ({status}).",
        }

    if status != "ok":
        raise RuntimeError(f"예상하지 못한 DB 조회 상태입니다: {status!r}")

    index_status = raw.get("index_status")
    if index_status not in _VALID_INDEX_STATUSES:
        raise ValueError(f"허용되지 않은 index_status입니다: {index_status!r}")

    vector_fresh = bool(raw.get("vector_fresh", False))
    revision = raw.get("revision")
    indexed_revision = raw.get("indexed_revision")
    category_code = raw.get("category_code")
    embedding_model = raw.get("embedding_model")

    # DB 상태가 ready여도 벡터 정합성(revision·해시·모델)이 맞아야 실제 검색 대상에 포함됩니다.
    searchable = index_status == "ready" and vector_fresh

    if searchable:
        summary = (
            f"보고서 {report_id}번({category_code})은 index_status='ready'이며 "
            f"벡터 정합성(revision {revision} == indexed_revision {indexed_revision})이 최신 상태입니다."
        )
    elif index_status == "ready" and not vector_fresh:
        summary = (
            f"보고서 {report_id}번({category_code})은 index_status='ready'이지만 "
            f"벡터 정합성(vector_fresh=False)이 맞지 않아 재색인 점검이 필요합니다."
        )
    else:
        summary = (
            f"보고서 {report_id}번({category_code})은 현재 index_status='{index_status}', "
            f"vector_fresh={vector_fresh} 상태여서 RAG 검색 대상이 아닙니다."
        )

    return {
        "status": "ok",
        "report_id": report_id,
        "category_code": category_code,
        "index_status": index_status,
        "revision": revision,
        "indexed_revision": indexed_revision,
        "vector_fresh": vector_fresh,
        "searchable": searchable,
        "embedding_model": embedding_model,
        "summary": summary,
    }