"""I-08: 단계별 증거와 실패 위치 후보. 자동 의미 판정을 주장하지 않는다."""
from pathlib import Path

def diagnose(row):
    if row['state']!='observed':
        code=row.get('error','')
        if row['state']=='dataset_changed':return 'Gold snapshot 변경'
        if code=='DB_UNAVAILABLE':return 'Retrieval / DB'
        if code=='RERANKER_UNAVAILABLE':return 'Rerank'
        if code in ('GPU_UNAVAILABLE','EMBEDDING_UNAVAILABLE'):return 'Embedding / GPU'
        if str(row.get('reason','')).startswith('rewrite'):return 'Rewrite'
        if code=='TOOL_CONTRACT_ERROR':return 'Tool / Validation'
        return 'LLM/계약 (마지막 성공 stage 확인: '+str(row.get('last_success_stage'))+')'
    before=row['before']['recall'];after=row['after']['recall']
    if before is None:return 'No-answer: Generation 사람 평가 필요'
    if before==0:return 'Retrieval miss (Rewrite lineage도 점검)'
    if after is not None and after<before:return 'Rerank miss'
    if 'generation' in row and row['generation'].get('status')!='completed':return 'Generation/Tool: 완료 상태·오류·trace 점검'
    return '검색 후보 확보; Faithfulness/Relevance/정답성 별도 검토'

def write_report(result):
    lines=['# Day30 단계별 평가 리포트','실제 실행 시 생성. 자동 근거 의미 평가가 아닙니다.','| Case | State | Original → search | Before → After IDs | 진단 |','|---|---|---|---|---|']
    for row in result['rows']:
        d=row.get('debug',{});q=' / '.join(d.get('query_search',[]));ids=lambda x:[a['report_id'] for a in d.get(x,[])]
        lines.append(f"| {row['case_id']} | {row['state']} | {row['question']} → {q} | {ids('before')} → {ids('after')} | {diagnose(row)} |".replace('\n',' '))
    lines.extend(['','- Gold는 부분 판정입니다. Recall/MRR/nDCG는 고정 Gold 기준입니다.','- 동일 후보 집합 Reranking은 전체 k에서 Recall이 동일할 수 있습니다. 순위 지표를 함께 봅니다.','- Faithfulness, Relevance, Correctness는 실제 응답과 원문을 사람이 대조하고 별도 기록합니다.'])
    Path('outputs/debug_report.md').write_text('\n'.join(lines),encoding='utf-8')
