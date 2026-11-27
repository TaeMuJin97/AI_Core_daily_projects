"""B-13/A-04/A-06: 모델의 자기신고가 아닌 Tool 실행 증거를 확인한다."""
import json,re
from pydantic import ValidationError
from app.schemas.agent import ModelAnswer, RagResult, StatusResult, AskResponse
from app.services.errors import ServiceError


def parse_answer(content):
    # JSON만 받는다. 형식이 잘못되면 성공으로 복구하지 않는다.
    try:
        if not isinstance(content,str):
            raise ValueError()
        return ModelAnswer.model_validate_json(content)
    except (ValidationError,ValueError,TypeError):
        raise ServiceError('OUTPUT_CONTRACT_ERROR','invalid_model_json') from None

def citation_ids(answer, allowed):
    # BEGIN B-13
    inline=set(re.findall(r'RPT-\d+',answer.answer))
    stated=set(answer.source_ids)
    return (len(stated)==len(answer.source_ids) and inline==stated and stated<=set(allowed)
            and all(re.fullmatch(r'RPT-[1-9][0-9]*',x) for x in stated))
    # END B-13

def check_tool_output(name,result):
    try:
        if name=='rag_search':
            obj=RagResult.model_validate(result)
            ids={s.source_id for s in obj.sources}
            if len(ids)!=len(obj.sources) or any(s.source_id!=f'RPT-{s.report_id}' for s in obj.sources):
                raise ValueError()
            if obj.status=='found' and (not ids or set(re.findall(r'RPT-\d+',obj.answer))!=ids):
                raise ValueError()
            if obj.status!='found' and (ids or re.search(r'RPT-\d+',obj.answer)):
                raise ValueError()
        elif name=='lookup_status':
            obj=StatusResult.model_validate(result)
            fields=[obj.category_code,obj.index_status,obj.revision,obj.embedding_fresh]
            if (obj.status=='found' and any(x is None for x in fields)) or (obj.status!='found' and any(x is not None for x in fields)):
                raise ValueError()
        else:
            raise ValueError()
        return obj.model_dump(exclude_none=True)
    except (ValidationError,ValueError,TypeError):
        raise ServiceError('TOOL_CONTRACT_ERROR','invalid_tool_output') from None


def trace_from_messages(messages,ledger):
    """AIMessage의 호출 요청과 ToolMessage 및 실제 실행 ledger를 3자 대조한다."""
    requested={}; seen=set(); traces=[]; observed=[]
    for msg in messages:
        if getattr(msg,'type',None)=='ai':
            for call in getattr(msg,'tool_calls',[]):
                cid=call.get('id')
                if not cid or cid in requested:
                    raise ServiceError('TOOL_CONTRACT_ERROR','duplicate_call_id')
                requested[cid]=call
        elif getattr(msg,'type',None)=='tool':
            cid=msg.tool_call_id
            if cid in seen or cid not in requested:
                raise ServiceError('TOOL_CONTRACT_ERROR','unmatched_call_id')
            seen.add(cid)
            entry=ledger.get(cid)
            # Schema 오류 등으로 Python 함수 본문에 진입하지 못한 ToolMessage는 실행 증거가 아니다.
            if entry is None:
                if getattr(msg,'status',None)=='error':
                    continue
                raise ServiceError('TOOL_CONTRACT_ERROR','missing_execution')
            try:
                result=json.loads(msg.content) if isinstance(msg.content,str) else None
            except ValueError:
                raise ServiceError('TOOL_CONTRACT_ERROR','invalid_tool_message') from None
            if entry['name']!=requested[cid]['name'] or entry['name']!=getattr(msg,'name',None) or result!=entry['result']:
                raise ServiceError('TOOL_CONTRACT_ERROR','message_execution_mismatch')
            if entry['name']=='lookup_status' and requested[cid].get('args',{}).get('report_id') != result.get('report_id'):
                raise ServiceError('TOOL_CONTRACT_ERROR','lookup_argument_mismatch')
            traces.append({'tool_call_id':cid,'tool':entry['name'],'status':result['status']})
            observed.append(entry)
    if set(ledger)-seen or set(requested)-seen:
        raise ServiceError('TOOL_CONTRACT_ERROR','unreturned_tool')
    return traces,observed


def expected_tools(question):
    # 완료 검증용 보수적 휴리스틱. 실행 경로는 이 함수로 고정하지 않는다.
    status=bool(re.search(r'인덱싱|인덱스\s*상태|revision|리비전|리비젼|embedding\s*(?:fresh|최신)|임베딩\s*최신|index_status|indexing|(?:보고서|report).*상태',question,re.I))
    content=bool(re.search(r'내용|핵심|요약|설명|근거|찾아|검색|비교|결론|content|summary|summari[sz]e',question,re.I))
    # '상태를 설명'은 상태 전용 요청일 수 있으므로 내용 표현이 명시된 경우만 복합 처리.
    if status:
        content=bool(re.search(r'내용|핵심|요약|근거|보고서.*(?:찾아|검색)|결론|content|summary|summari[sz]e',question,re.I))
        return {'lookup_status','rag_search'} if content else {'lookup_status'}
    return {'rag_search'}


def finalize(request_id,question,answer,traces,observed,latency_ms,category=None):
    from app.rag.ids import explicit_ids
    ids=explicit_ids(question)
    allowed={}; statuses={}
    for item in observed:
        result=item['result']
        if result['status']!='found':
            continue
        if item['name']=='rag_search':
            for source in result['sources']:
                if (category is not None and source['category_code']!=category) or (ids and source['report_id'] not in ids):
                    raise ServiceError('TOOL_CONTRACT_ERROR','source_scope')
                allowed[source['source_id']]=source
        else:
            statuses[result['report_id']]=result
    if not citation_ids(answer,allowed):
        raise ServiceError('OUTPUT_CONTRACT_ERROR','agent_citation')
    required=expected_tools(question)
    executed={item['name'] for item in observed if item['result']['status'] in ('found','not_found')}
    found={item['name'] for item in observed if item['result']['status']=='found'}
    tools_observed=required<=executed
    cited=[allowed[x] for x in answer.source_ids]
    rag_ok=bool(cited) and (not ids or ids<={s['report_id'] for s in cited})
    status_ok=bool(statuses) and (not ids or ids<=set(statuses))
    # 모델의 자연어 상태 주장 대신 서버가 조회한 원본 필드를 함께 제공한다.
    # 최종 문장과 원문 의미 일치는 사람 평가가 필요하다.
    complete=tools_observed and required<=found and ('rag_search' not in required or rag_ok) and ('lookup_status' not in required or status_ok)
    if any(item['result']['status']=='error' for item in observed):
        state='incomplete'
    elif answer.status=='completed' and complete:
        state='completed'
    elif not tools_observed or (len(required)>1 and bool(found & required) and not complete):
        state='incomplete'
    elif answer.status=='insufficient_evidence' or not (found & required):
        state='insufficient_evidence'
    else:
        state='incomplete'
    text=answer.answer
    if state=='insufficient_evidence':
        text='요청에 답할 충분한 보고서 근거 또는 조회 결과가 없습니다.';cited=[]
    elif state=='incomplete':
        text='요청에 필요한 도구 결과 또는 근거가 충분히 확인되지 않아 작업을 완료하지 못했습니다.';cited=[]
    if statuses and state=='completed':
        # 조회값은 실제 Tool output을 그대로 사용. 모델이 임의 숫자를 작성하지 않도록 prompt에서도 요구.
        lines=[f"보고서 {r}: index_status={s['index_status']}, revision={s['revision']}, embedding_fresh={str(s['embedding_fresh']).lower()}" for r,s in sorted(statuses.items()) if not ids or r in ids]
        if required=={'lookup_status'}:
            text='\n'.join(lines);cited=[]
        else:
            text+='\n\n[실제 DB 상태]\n'+'\n'.join(lines)
    return AskResponse(request_id=request_id,status=state,answer=text,sources=cited,tool_trace=traces,
        validation={'citations_match_context':True,'required_tools_observed':tools_observed},latency_ms=float(latency_ms)).model_dump()
