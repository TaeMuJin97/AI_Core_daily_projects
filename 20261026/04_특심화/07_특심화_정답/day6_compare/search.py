"""실습06의 K 실험을 종합 프로젝트로 옮깁니다. test는 함수 인자로도 받지 않습니다."""
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor
from preprocessing import build_pipeline
from evaluate import regression_metrics,classification_metrics
from course_io import validate_k

def search_k(d,candidates=(1,3,5,9,15)):
    """task,K,scale,weights,p,metric,train_score,valid_score의 10행 표를 만든다.
    회귀/분류는 서로 다른 y와 지표를 사용한다. 조건은 standard,uniform,p=2로 고정한다.
    """
    # 정답 해설 D6-07-H4
    rows=[]
    for task,ytr,yva,cls,fn,key in [
        ('classification',d.yc_train,d.yc_valid,KNeighborsClassifier,classification_metrics,'F1'),
        ('regression',d.yr_train,d.yr_valid,KNeighborsRegressor,regression_metrics,'RMSE_ms')]:
        for k in candidates:
            validate_k(k,len(d.X_train))
            m=build_pipeline(cls(n_neighbors=k,weights='uniform',p=2)).fit(d.X_train,ytr)
            rows.append({'task':task,'K':int(k),'scale':'standard','weights':'uniform','p':2,
                'metric':key,'train_score':fn(ytr,m.predict(d.X_train))[key],
                'valid_score':fn(yva,m.predict(d.X_valid))[key]})
    return pd.DataFrame(rows)

def choose_k(table):
    result={}
    for task in ['classification','regression']:
        p=table.loc[table.task==task].sort_values(['valid_score','K'],
                    ascending=[task=='regression',True],kind='stable')
        if p.empty: raise ValueError('K 탐색표에 두 문제의 결과가 모두 필요합니다.')
        result[task]=int(p.iloc[0]['K'])
    return result
