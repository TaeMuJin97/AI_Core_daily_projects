"""I-07: Gold는 이 평가 모듈에서만 읽는다. 실제 질의 실행 시 유료 Rewrite 호출이 발생할 수 있다."""
import argparse,json,hashlib,math
from pathlib import Path
from app.services.metrics import Meter

def scores(ranked,grades,k):
    # 미판정 문서는 이번 제한적 평가에서 0으로 취급. no-answer는 N/A.
    ranked=list(dict.fromkeys(ranked))[:k]
    relevant={int(i) for i,g in grades.items() if g>0}
    if not relevant:return {'recall':None,'mrr':None,'ndcg':None}
    dcg=sum((2**grades.get(str(r),0)-1)/math.log2(i+2) for i,r in enumerate(ranked))
    ideal=sum((2**g-1)/math.log2(i+2) for i,g in enumerate(sorted(grades.values(),reverse=True)[:k]))
    return {'recall':len(relevant&set(ranked))/len(relevant),'mrr':next((1/i for i,r in enumerate(ranked,1) if r in relevant),0.0),'ndcg':dcg/ideal if ideal else None}

def gold_current(repo,case):
    # 고정 ID는 검색에 전달하지 않고, 평가 전에 데이터 변경 여부만 SELECT로 확인.
    for item in case['evidence']:
        with repo.db.read() as conn:
            from sqlalchemy import text
            row=conn.execute(text('SELECT title,content,overview,revision FROM public.report_read_view WHERE report_id=:rid'),{'rid':item['report_id']}).mappings().first()
        if not row or row['revision']!=item['revision'] or row['title']!=item['title']:
            return False
        for key in ['content','overview']:
            if hashlib.sha256(row[key].encode()).hexdigest()!=item[key+'_sha256']:return False
    return True

def evaluate(runtime,cases,k,run_generation=False):
    from app.schemas.agent import AskRequest
    from app.services.errors import ServiceError
    rows=[]
    candidate_k=max(k,runtime.settings.retrieve_k)
    for case in cases:
        row={'case_id':case['case_id'],'question':case['question'],'mode':'live_attempt','gold_ids':[int(x) for x in case['grades']]}
        meter=Meter(runtime.settings)
        try:
            if not gold_current(runtime.repo,case):
                row['state']='dataset_changed';rows.append(row);continue
            _,info=runtime.pipeline.retrieve(case['question'],case['category_code'],candidate_k,meter)
            before=[x['report_id'] for x in info['before']];after=[x['report_id'] for x in info['after']]
            row.update(state='observed',before=scores(before,case['grades'],k),after=scores(after,case['grades'],k),debug=info,metrics=meter.summary())
        except ServiceError as exc:
            row.update(state='failed',error=exc.code,reason=exc.reason,metrics=meter.summary())
            row['last_success_stage']=next((stage['stage'] for stage in reversed(meter.stages)),None)
        if run_generation and row['state']=='observed':
            gm=Meter(runtime.settings)
            try:
                response=runtime.agent.ask(case['case_id'],AskRequest(question=case['question'],category_code=case['category_code']),gm)
                row['generation']={'state':'observed','status':response['status'],'answer':response['answer'],'sources':response['sources'],'tool_trace':response['tool_trace'],
                    'faithfulness':None,'relevance':None,'correctness':None,'human_review':'pending','metrics':gm.summary()}
            except ServiceError as exc:
                row['generation']={'state':'failed','error':exc.code,'reason':exc.reason,'metrics':gm.summary(),'faithfulness':None,'relevance':None,'correctness':None}
        rows.append(row)
    aggregates={}
    for side in ['before','after']:
        aggregates[side]={}
        for key in ['recall','mrr','ndcg']:
            vals=[r[side][key] for r in rows if r.get('state')=='observed' and r[side][key] is not None]
            aggregates[side][key]={'mean':sum(vals)/len(vals) if vals else None,'n':len(vals)}
    return {'mode':'live_attempt','k':k,'candidate_k':candidate_k,'rows':rows,'aggregates':aggregates,'n_total':len(rows),'n_observed':sum(r.get('state')=='observed' for r in rows),'n_failed':sum(r.get('state')=='failed' for r in rows),'n_dataset_changed':sum(r.get('state')=='dataset_changed' for r in rows),'n_generation_failed':sum(r.get('generation',{}).get('state')=='failed' for r in rows)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--gold',default='data/evaluation/gold.json');parser.add_argument('--k',type=int,default=3);parser.add_argument('--allow-paid-llm',action='store_true');parser.add_argument('--generation',action='store_true');args=parser.parse_args()
    if not args.allow_paid_llm:parser.error('Rewrite/Generation 유료 호출 동의: --allow-paid-llm 필요')
    if not 1<=args.k<=30:parser.error('k는 1~30')
    from app.core.runtime import Runtime
    runtime=Runtime()
    try:
        runtime.health()
        cases=json.loads(Path(args.gold).read_text(encoding='utf-8'))
        result=evaluate(runtime,cases,args.k,args.generation)
        path=Path('outputs/retrieval_eval.json');path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        from app.evaluation.debug_report import write_report
        write_report(result)
        print(json.dumps(result['aggregates'],ensure_ascii=False,indent=2))
    finally:runtime.close()
if __name__=='__main__':main()
