"""T-01~10: 실제 교실 환경 검증. python -m scripts.verify_live --allow-paid-llm 선택 시 유료 실행."""
import argparse,json,os
from pathlib import Path
from app.core.runtime import Runtime
from app.services.errors import ServiceError
from app.services.metrics import Meter
from app.schemas.agent import AskRequest
from app.rag.documents import source_of
from app.services.validator import check_tool_output

OUT=Path('outputs')
def save(name,data):
    OUT.mkdir(exist_ok=True)
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--allow-paid-llm',action='store_true')
    p.add_argument('--report-id',type=int,help='유효 보고서 ID (생략 시 .env의 DAY30_REPORT_ID)')
    p.add_argument('--missing-report-id',type=int,help='미존재 ID (생략 시 .env의 DAY30_MISSING_ID)')
    args=p.parse_args()
    checks={};runtime=None;before=None;fail=False
    def check(t,fn):
        nonlocal fail
        try:
            details=fn();checks[t]={'state':'observed','details':details}
            return details
        except Exception as e:
            checks[t]={'state':'failed','error':e.envelope() if isinstance(e,ServiceError) else {'code':type(e).__name__}}
            fail=True
    try:
        runtime=Runtime()  # load_settings()가 .env를 먼저 읽는다.
        # 명시한 CLI 값 > 현재 환경변수/.env > 기존 예시 기본값.
        try:
            if args.report_id is None: args.report_id=int(os.getenv('DAY30_REPORT_ID','63'))
            if args.missing_report_id is None: args.missing_report_id=int(os.getenv('DAY30_MISSING_ID','999999'))
            if not (1 <= args.report_id <= 9223372036854775807 and
                    1 <= args.missing_report_id <= 9223372036854775807 and
                    args.report_id != args.missing_report_id):
                raise ValueError()
        except (ValueError,TypeError):
            raise ServiceError('CONFIG_INVALID','invalid_test_report_ids') from None
        if check('T-01',runtime.health) is None:return 1
        before=check('T-02-before',runtime.repo.snapshot)
        # 유료 호출 전에 실제 ID를 읽기 전용으로 확인한다.
        def check_ids():
            found=runtime.repo.lookup(args.report_id)
            missing=runtime.repo.lookup(args.missing_report_id)
            if found['status']!='found' or not found.get('embedding_fresh') or missing['status']!='not_found':
                raise ServiceError('CONFIG_INVALID','test_report_ids_not_eligible')
            return {'report_id':args.report_id,'missing_report_id':args.missing_report_id}
        if check('T-01-test-ids',check_ids) is None:return 1
        def vector_check():
            meter=Meter(runtime.settings)
            vec=runtime.embedder.encode('RAG 근거 인용',meter)
            return {'device':str(runtime.embedder.model.device),'dimension':len(vec),'norm_squared':sum(x*x for x in vec),'finite':all(__import__('math').isfinite(x) for x in vec),'measurement':meter.summary()}
        check('T-03-vector',vector_check)
        m=Meter(runtime.settings)
        q=f'보고서 {args.report_id}의 핵심 내용'
        def retrieval():
            docs,debug=runtime.pipeline.retrieve(q,None,runtime.settings.retrieve_k,m)
            if not docs:raise ServiceError('EMBEDDING_UNAVAILABLE','report_not_eligible')
            return {'debug':debug,'sources':[source_of(d) for d in docs],'measurement':m.summary()}
        if not args.allow_paid_llm and runtime.pipeline.optimizer is not None:
            # 무료 확인은 실제 기본 검색만 수행; Rewrite 유료 호출 차단.
            runtime.pipeline.optimizer=None
        check('T-03/T-05',retrieval)
        from app.tools.db_tool import make_db_tool
        from app.tools.rag_tool import make_rag_tool
        def direct_lookup():
            meter=Meter(runtime.settings)
            tool=make_db_tool(runtime.repo,q,meter)
            msg=tool.invoke({'name':'lookup_status','args':{'report_id':args.report_id},'id':'direct-db','type':'tool_call'})
            data=json.loads(msg.content)
            if data['status']!='found' or 'direct-db' not in meter.ledger:raise ServiceError('TOOL_CONTRACT_ERROR')
            return data
        check('T-06-lookup',direct_lookup)
        if args.allow_paid_llm:
            def direct_rag():
                meter=Meter(runtime.settings)
                tool=make_rag_tool(runtime.pipeline,runtime.settings,q,None,meter)
                msg=tool.invoke({'name':'rag_search','args':{'query':q,'k':min(3,runtime.settings.retrieve_k)},'id':'direct-rag','type':'tool_call'})
                data=json.loads(msg.content)
                if data['status']!='found' or 'direct-rag' not in meter.ledger:raise ServiceError('TOOL_CONTRACT_ERROR')
                return {'status':data['status'],'sources':data['sources'],'metrics':meter.summary()}
            check('T-04/T-06-rag',direct_rag)
        if args.allow_paid_llm:
            for name,q in [('rag_only',f'보고서 {args.report_id}의 핵심 내용을 설명해 줘.'),('db_only',f'보고서 {args.report_id}의 인덱싱 상태와 revision을 알려 줘.'),('both',f'보고서 {args.report_id}의 핵심 내용과 인덱싱 상태를 함께 설명해 줘.'),('no_answer','화성의 낙타 전용 미용실 운영시간을 알려 줘.'),('missing',f'보고서 {args.missing_report_id}의 현재 인덱싱 상태를 확인해 줘.')]:
                def ask():
                    meter=Meter(runtime.settings);out=runtime.agent.ask(name,AskRequest(question=q),meter)
                    wanted={'rag_only':{'rag_search'},'db_only':{'lookup_status'},'both':{'rag_search','lookup_status'}}.get(name)
                    if wanted and (out['status']!='completed' or not wanted<={x['tool'] for x in out['tool_trace'] if x['status']=='found'}):
                        raise ServiceError('TOOL_CONTRACT_ERROR','acceptance_not_met')
                    if not wanted and out['status']!='insufficient_evidence':raise ServiceError('TOOL_CONTRACT_ERROR','expected_no_answer')
                    # 답변 원문 대신 검증용 metadata/trace만 기본 저장. 실제 답변은 로컬 화면에서 사람이 검토.
                    print(name,out['status'],out['answer'])  # 로컬 화면에서만 확인; 외부 공유 시 마스킹
                    return {k:v for k,v in out.items() if k!='answer'}|{'metrics':meter.summary(),'human_review':'pending'}
                check('T-07/T-09/T-10-'+name,ask)
        else:checks['paid_tests']={'state':'not_run','reason':'--allow-paid-llm 미지정'}
    except Exception as e:
        checks['setup_or_execution']={'state':'failed','error':e.envelope() if isinstance(e,ServiceError) else {'code':type(e).__name__}}
        fail=True
    finally:
        if runtime is not None:
            if before is not None:
                after=check('T-02-after',runtime.repo.snapshot)
                checks['T-02-unchanged']={'state':'observed' if after==before else 'failed','equal':after==before}
                fail=fail or after!=before
            runtime.close()
        save('live_checks.json',{'mode':'live_attempt','checks':checks,'human_review':'pending','note':'observed는 측정됨을 뜻하며 자동 합격 인증이 아님. T-08 HTTP는 Postman 별도.'})
    return 1 if fail else 0
if __name__=='__main__':raise SystemExit(main())
