"""B-06: 실제 VIEW 원문을 LangChain Document와 Metadata로 보존."""
from langchain_core.documents import Document
from app.services.errors import ServiceError

def to_document(row):
    # TODO B-06: Document의 page_content에는 row[content]를, metadata에는 source_id=RPT-번호, report_id/title/category_code/revision/overview/distance를 넣으세요.
    raise ServiceError('NOT_IMPLEMENTED','B-06')
    # END TODO B-06

def source_of(doc):
    return {k:doc.metadata[k] for k in ('source_id','report_id','title','category_code','revision')}
