"""Day5 실습 08 · 이미 생성한 프로젝트 산출물을 읽어 검증합니다.
기본 검증은 joblib을 읽지 않습니다. 별도 프로세스 복원은 신뢰를 명시한 경우만 실행합니다.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import numpy as np
import pandas as pd

LEVEL="applied"
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_PROJECT=ROOT/"ex07_project"/"02_응용"/"day5_ml"
FEATURES=["input_chars","allowed_tools","task_type","priority"]
EXPECTED_NAMES=["num__input_chars","num__allowed_tools","cat__task_type_qa",
    "cat__task_type_research","cat__task_type_summary","cat__priority_high",
    "cat__priority_low","cat__priority_normal"]

def read_bundle(project):
    """제공: 사람이 검토할 CSV·JSON만 읽고 각 산출물을 반환합니다."""
    project=Path(project);out=project/"outputs"
    required=["split_manifest.csv","split_order.json","feature_names.json","validation_features.csv",
        "validation_predictions.csv","validation_metrics.json","preprocessing_state.json",
        "protocol_log.json","run_metadata.json","artifact_manifest.json","pipeline.joblib"]
    missing=[n for n in required if not (out/n).is_file()]
    if missing:raise FileNotFoundError(f"실습 07을 먼저 실행하세요. 없는 결과: {missing}")
    # 내용이 JSON인 파일에만 json.loads를 사용합니다. pipeline.joblib은 존재/해시만 검사합니다.
    j=lambda n:json.loads((out/n).read_text(encoding="utf-8"))
    frame=lambda n:pd.read_csv(out/n,dtype={"request_id":str})
    return {"project":project,"out":out,"manifest":frame("split_manifest.csv"),
        "order":j("split_order.json"),"names":j("feature_names.json"),
        "ready":pd.read_csv(out/"validation_features.csv",index_col="request_id"),
        "pred":frame("validation_predictions.csv"),"metrics":j("validation_metrics.json"),
        "state":j("preprocessing_state.json"),"events":j("protocol_log.json"),
        "meta":j("run_metadata.json"),"hashes":j("artifact_manifest.json"),
        "raw":pd.read_csv(project/"data"/"requests.csv",dtype={"request_id":str}).set_index("request_id")}

def check_records(bundle):
    """Day5 100행 기준 산출물의 분할과 예측 ID/정답 정렬을 독립 검증.
    manifest: 고유100개, train60/valid20/test20. order도 manifest와 소속이 일치해야 합니다.
    pred의 ID 순서=order[valid], y_true=원본 valid 정답, ready의 index/열 이름도 일치.
    실패는 ValueError, 정상은 True. 행 개수만 검사하지 않습니다.
    """
    # 제공: 결과 읽기/앞 단원 재사용 코드.
    m=bundle["manifest"];pred=bundle["pred"];order=bundle["order"];raw=bundle["raw"]
    if list(m.columns)!=["request_id","split"] or not m["request_id"].is_unique:
        raise ValueError("분할표 열/중복 ID 오류")
    if len(m)!=100 or m["split"].value_counts().to_dict()!={"train":60,"valid":20,"test":20}:
        raise ValueError("분할 수 오류")
    if set(m["request_id"])!=set(raw.index):raise ValueError("원본 ID와 분할표 불일치")
    if set(order)!={"train","valid","test"}:raise ValueError("분할 순서 기록 누락")
    for name in order:
        if len(order[name])!=len(set(order[name])) or set(order[name])!=set(m.loc[m["split"]==name,"request_id"]):
            raise ValueError("순서 기록과 분할 소속 불일치")
    if pred["request_id"].tolist()!=order["valid"]:raise ValueError("검증 예측 ID 정렬 오류")
    if not np.array_equal(pred["y_true"].to_numpy(),raw.loc[order["valid"],"failed"].to_numpy()):
        raise ValueError("검증 정답이 원본과 다름")
    if bundle["names"]!=EXPECTED_NAMES:raise ValueError("특성명/순서 오류")
    ready=bundle["ready"]
    if ready.index.tolist()!=order["valid"] or list(ready.columns)!=bundle["names"]:
        raise ValueError("변환 행렬의 ID/열 이름 오류")
    if ready.shape!=(20,8) or not np.isfinite(ready.to_numpy()).all():raise ValueError("변환 행렬 오류")
    return True

def check_training_evidence(bundle):
    """제공: train 통계 출처와 실행 기록, valid 수치를 재계산합니다.
    이 기록 검사 자체가 악의적 코드/허위 기록을 완전히 증명·차단하지는 않습니다.
    실제 fit 호출 검사와 사람의 코드리뷰가 함께 필요합니다.
    """
    meta=bundle["meta"];order=bundle["order"];state=bundle["state"];raw=bundle["raw"]
    if meta["fit_ids"]!=order["train"]:raise ValueError("fit ID 기록 오류")
    if meta["feature_input"]!=FEATURES or meta["test_model_calls"]!=0:raise ValueError("입력/시험 정책 오류")
    for event in bundle["events"]:
        if event["split"]=="test":raise ValueError("test 모델 호출 기록")
        if event["operation"]=="fit" and event["split"]!="train":raise ValueError("train 외 학습 기록")
    train=raw.loc[order["train"],FEATURES[:2]]
    medians=train.median().to_numpy()
    if not np.allclose(state["numeric_medians"],medians) or state["scaler_seen"]!=60:
        raise ValueError("train 통계 근거 오류")
    filled=train.fillna(train.median()).to_numpy()
    if not np.allclose(state["scaler_mean"],filled.mean(axis=0)) or not np.allclose(state["scaler_scale"],filled.std(axis=0)):
        raise ValueError("scaler 학습 통계 오류")
    p=bundle["pred"]
    if not p["y_pred"].isin([0,1]).all():raise ValueError("예측 범주 오류")
    actual={"correct":int((p["y_true"]==p["y_pred"]).sum()),"total":len(p),
        "accuracy":float((p["y_true"]==p["y_pred"]).mean()),
        "found_failed":int(((p["y_true"]==1)&(p["y_pred"]==1)).sum()),
        "total_failed":int((p["y_true"]==1).sum())}
    if bundle["metrics"]!=actual:raise ValueError("기록한 지표와 예측 파일이 다름")
    if actual!={"correct":14,"total":20,"accuracy":0.7,"found_failed":0,"total_failed":6}:
        raise ValueError("Day5 기준선 기대 결과와 다름; 다음 수업 모델과 혼합하지 마세요.")
    return True

def check_hashes(bundle):
    """제공: 파일 변화 탐지. 해시는 파일의 신뢰성/안전성을 증명하지 않습니다."""
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if digest(bundle["project"]/"data"/"requests.csv")!=bundle["meta"]["input_sha256"]:
        raise ValueError("원본 해시 불일치")
    for name,wanted in bundle["hashes"].items():
        if Path(name).name!=name or digest(bundle["out"]/name)!=wanted:
            raise ValueError(f"산출물 변경 감지: {name}")
    return True

def fresh_restore(project,trusted=False):
    """신뢰 승인이 있어야 restore_check.py를 현재 실행기의 새 프로세스로 실행합니다.
    인자 리스트로 subprocess.run(check=True,capture_output=True,text=True,encoding='utf-8').
    반환값은 복원 스크립트의 JSON stdout을 파싱한 dict입니다. shell=True는 사용하지 않습니다.
    """
    # TODO D5-08-A1: 위 함수 설명의 입력·반환·검사 조건을 구현하세요.
    raise NotImplementedError("D5-08-A1를 완성하세요.")

def boundary_checks(project):
    """프로젝트 checks.validate_features를 호출해 최소 두 실패 조건을 검사합니다.
    누락 priority와 전체 결측 train task_type은 ValueError, 미지 범주는 정상이어야 합니다.
    반환: missing_rejected, all_missing_train_rejected, unknown_allowed 세 bool dict.
    예외가 나지 않으면 그 조건을 True로 표시하지 않습니다.
    """
    # 제공: 결과 읽기/앞 단원 재사용 코드.
    path=Path(project)/"checks.py"
    spec=importlib.util.spec_from_file_location("day5_project_contract",path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    new=pd.DataFrame({"input_chars":[800.,np.nan],"allowed_tools":[2.,3.],
        "task_type":["qa","translation"],"priority":["normal","urgent"]})
    result={}
    cases={"missing_rejected":(new.drop(columns="priority"),False),
           "all_missing_train_rejected":(new.assign(task_type=np.nan),True)}
    for name,(frame,training) in cases.items():
        try:mod.validate_features(frame,training=training)
        except ValueError:result[name]=True
        else:result[name]=False
    result["unknown_allowed"]=mod.validate_features(new).shape==(2,4)
    if not all(result.values()):raise AssertionError("경계/실패 검사에서 기대한 오류가 발생하지 않음")
    return result

def review_project(project=DEFAULT_PROJECT,trusted=False):
    bundle=read_bundle(project)
    check_records(bundle);check_training_evidence(bundle);check_hashes(bundle)
    result={"artifacts":"PASS","rows_valid":20,"features":8,"test_model_calls":0,
        "manual_review":"문제정의·해석·README 재현·개인 설명·Git 이력은 별도 확인"}
    if LEVEL in {"applied","advanced"}:
        result["fresh_restore"]=fresh_restore(project,True) if trusted else "SKIPPED: 신뢰 승인 후 실행"
    if LEVEL=="advanced":result["boundary_checks"]=boundary_checks(project)
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
    parser.add_argument("--trust-local-model",action="store_true")
    args=parser.parse_args()
    print(json.dumps(review_project(args.project,args.trust_local_model),ensure_ascii=False,indent=2))
