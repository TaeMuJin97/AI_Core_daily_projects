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
        # BEGIN B-05
        # 실제 pgvector cosine distance(<=>) 오름차순; 원문과 벡터를 같은 SELECT snapshot에서 조회.
        sql = text("""SELECT v.report_id,v.title,v.content,v.overview,v.category_code,v.revision,
            e.embedding OPERATOR(public.<=>) CAST(:vec AS public.vector) AS distance
            """+JOIN+' WHERE '+FRESH+"""
            AND (CAST(:cat AS text) IS NULL OR v.category_code=:cat)
            AND (CAST(:rid AS bigint) IS NULL OR v.report_id=:rid)
            ORDER BY distance ASC, v.report_id ASC LIMIT :k""")
        params = {'vec':'['+','.join(str(float(x)) for x in vector)+']','model':MODEL,
                  'cat':category_code,'rid':report_id,'k':top_k}
        with self.db.read() as conn:
            return [dict(row) for row in conn.execute(sql,params).mappings()]
        # END B-05
    def lookup(self, report_id):
        # BEGIN B-10
        sql = text('SELECT r.report_id,c.code AS category_code,r.index_status,r.revision, '
            'COALESCE(('+FRESH+'),false) AS embedding_fresh '
            'FROM public.reports r JOIN public.report_categories c ON c.category_id=r.category_id '
            'LEFT JOIN public.report_embeddings e ON e.report_id=r.report_id WHERE r.report_id=:rid')
        with self.db.read() as conn:
            row = conn.execute(sql,{'rid':report_id,'model':MODEL}).mappings().first()
            return {'status':'found',**dict(row)} if row else {'status':'not_found','report_id':report_id}
        # END B-10
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
