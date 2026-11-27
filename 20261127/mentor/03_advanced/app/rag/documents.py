"""B-06: 실제 VIEW 원문을 LangChain Document와 Metadata로 보존."""
from langchain_core.documents import Document

def to_document(row):
    # BEGIN B-06
    return Document(page_content=row['content'],metadata={
        'source_id':f"RPT-{row['report_id']}",'report_id':row['report_id'],
        'title':row['title'],'category_code':row['category_code'],'revision':row['revision'],
        'overview':row['overview'],'distance':float(row['distance'])})
    # END B-06

def source_of(doc):
    return {k:doc.metadata[k] for k in ('source_id','report_id','title','category_code','revision')}
