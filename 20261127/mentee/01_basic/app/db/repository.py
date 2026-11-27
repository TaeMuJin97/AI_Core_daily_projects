"""B-03/B-05/B-10: 고정 SELECT와 bind parameter만 사용. SQL을 모델에 노출하지 않는다."""
from sqlalchemy import text
from app.services.errors import ServiceError
from app.core.settings import MODEL

CATEGORIES = {'EXPERIMENT','DAILY_WORK','RESEARCH_PLAN','DATA_PROCESSING','PROMPT','MEETING'}
# PostgreSQL 내장 sha256(bytea): 기존 UTF-8 SHA-256과 동일. 신규 extension 불필요.
FRESH = """r.index_status = 'ready' AND e.model_name = :model
AND e.indexed_revision = r.revision AND public.vector_dims(e.embedding) = 384
AND public.vector_norm(e.embedding) > 0
AND e.overview_hash = encode(sha256(convert_to(r.overview,'UTF8')),'hex')"""
JOIN = """FROM public.reports r JOIN public.report_embeddings e ON e.report_id=r.report_id
JOIN public.report_read_view v ON v.report_id=r.report_id"""
TABLES = ('report_categories','reports','report_embeddings','experiment_reports',
          'daily_work_reports','research_plans','data_processing_reports','prompt_reports','prompt_versions','meeting_minutes')

class Repository:
    def __init__(self, db):
        self.db = db
    def preflight(self):
        with self.db.read() as conn:
            db = conn.execute(text('SELECT current_database()')).scalar_one()
            extension = conn.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'")).scalar_one_or_none()
            codes = set(conn.execute(text('SELECT code FROM public.report_categories')).scalars())
            if db != 'report_agent_lab' or not extension or codes != CATEGORIES:
                raise ServiceError('DB_UNAVAILABLE')
            count = conn.execute(text('SELECT count(*) '+JOIN+' WHERE '+FRESH),{'model':MODEL}).scalar_one()
            return {'db':'ready','database':db,'pgvector':extension,'categories':sorted(codes),'eligible_vectors':count}
    def candidates(self, vector, category_code, top_k, report_id=None):
        # TODO B-05: SELECT에 VIEW 필드와 embedding cosine distance(<=>)를 포함하세요. 고정 JOIN/FRESH를 사용하고 :vec, :cat, :rid, :k, :model 바인딩을 적용해 distance 오름차순 TOP-k를 반환하세요. SQL 문자열에 사용자 입력을 직접 넣지 마세요.
        raise ServiceError('NOT_IMPLEMENTED','B-05')
        # END TODO B-05
    def lookup(self, report_id):
        # TODO B-10: reports와 report_categories JOIN, report_embeddings LEFT JOIN을 사용하세요. WHERE report_id=:rid, FRESH의 COALESCE(false)로 최신성 검사. 실제 행이면 found, 없으면 not_found 반환.
        raise ServiceError('NOT_IMPLEMENTED','B-10')
        # END TODO B-10
    def snapshot(self):
        # 고정된 테이블 목록만 사용. 내용/비밀번호를 출력하지 않고 row count와 digest만 저장.
        with self.db.read() as conn:
            conn.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ'))
            result = {}
            for table in TABLES:
                sql = text("SELECT count(*) AS count, encode(sha256(convert_to(COALESCE(string_agg(j, E'\\n' ORDER BY j),''),'UTF8')),'hex') AS sha256 "
                           f'FROM (SELECT row_to_json(t)::text AS j FROM public.{table} t) s')
                result[table] = dict(conn.execute(sql).mappings().one())
            return result
