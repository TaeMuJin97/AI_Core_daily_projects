"""T-02/T-03: SQL/parameter shape only. DB transaction and actual pgvector execution require Live check."""
from contextlib import contextmanager
from app.db.repository import Repository
class Rows:
    def mappings(self):return self
    def __iter__(self):return iter([{'report_id':63,'distance':0.2}])
    def first(self):return {'report_id':63,'index_status':'ready','revision':1,'embedding_fresh':True,'category_code':'RESEARCH_PLAN'}
class FakeDB:
    def __init__(self):self.calls=[]
    @contextmanager
    def read(self):yield self
    def execute(self,sql,params=None):self.calls.append((str(sql),params));return Rows()
def test_T03_query_contract():
    db=FakeDB();repo=Repository(db)
    assert repo.candidates([1.0]+[0.0]*383,'RESEARCH_PLAN',8,63)[0]['report_id']==63
    sql,params=db.calls[-1]
    for token in ["r.index_status = 'ready'",'e.indexed_revision = r.revision','public.vector_dims(e.embedding) = 384','sha256(convert_to','e.model_name = :model','OPERATOR(public.<=>)','v.category_code=:cat','v.report_id=:rid','ORDER BY distance ASC','LIMIT :k']:
        assert token in sql
    assert params['rid']==63 and params['cat']=='RESEARCH_PLAN' and params['k']==8 and 'RESEARCH_PLAN' not in sql
def test_T06_lookup_contract():
    db=FakeDB();result=Repository(db).lookup(63)
    sql,params=db.calls[-1]
    assert result['status']=='found' and 'LEFT JOIN public.report_embeddings' in sql and 'r.report_id=:rid' in sql and params['rid']==63
