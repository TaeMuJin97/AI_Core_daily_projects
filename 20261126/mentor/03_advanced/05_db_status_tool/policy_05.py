"""경계값·오류/권한 정책: Advanced · Day29."""

def enforce_read_policy(raw: dict, allowed: set[str]) -> dict:
    """앱 Category 정책. 실제 사용자 인증/소유권 ACL로 표현하지 마세요."""
    # 해설 D29-05-A-04: 보고서 상태는 pending/ready/failed이고 제출 여부가 아닙니다.
    # 검수 기준: ready 문자열뿐 아니라 Model·Revision·Overview Hash가 일치하는지 검증합니다.
    if raw.get('status')!='ok':return {'status':'not_found'}
    if raw['category_code'] not in allowed:return {'status':'not_found_or_forbidden'}
    return {'report_id':raw['report_id'],'index_status':raw['index_status'],
            'revision':raw['revision'],'vector_fresh':raw['vector_fresh']}

