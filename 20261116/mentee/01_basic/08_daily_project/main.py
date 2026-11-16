"""
==============================================================================
[실습 보고서: Day 21 실습 08 - AI 지식 답변 생성기 v1 (08_daily_project/main.py)]
1. 실험 목적:
   - 05교시에서 Development 세트(D01~D03)로 설계하고 고정한 프롬프트 번들(frozen_bundle.json)을 불러와,
     최종 확인용 Holdout 세트(H01~H03)에서 A/B 성능을 공정하게 검증하고 종합 리포트를 생성함.
2. 핵심 아키텍처 개념:
   - 프롬프트 동결(Prompt Freezing)과 과적합 방지 (D21-08-B01):
     Holdout(H01~H03) 결과를 보고 프롬프트 규칙을 다시 고치면 평가 데이터에 맞춰 답을 끼워 맞추는
     데이터 누수(Data Leakage)가 발생함. 따라서 05교시 산출물(frozen_bundle.json)을 수정 없이 그대로 읽고,
     필수 버전 키(context_version, schema_version, variants A/B)의 무결성만 검증함.
   - Holdout 평가 케이스 검증 (D21-08-B02):
     H01(단일 근거 응답), H02(정보 부족 응답), H03(다중 근거 101·102·103 종합 응답) 세 질문만 선택하며,
     채점 기준인 expected_behavior가 프롬프트 입력에 유출되지 않도록 분리함.
   - 종합 리포트 및 상태 분리 집계 (D21-08-B03):
     첫 응답(attempt == 1) 기준으로 미실행(not_run)과 사람 미평가(evidence_ok is None)를 0점(False)이나
     통과(True)로 둔갑시키지 않고 그대로 남기며, 최대 시도 횟수가 2회 이하(max_attempt <= 2)인지 검증함.
==============================================================================
"""
"""Day21 실습 08: AI 지식 답변 생성기 v1. 실행: python main.py"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, run
from coursekit.prompting import make_bundle

# 기준: Day21 PPT 64~72장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.
from coursekit.experiments import prepare_experiment, review_experiment, summarize, write_summary
from coursekit.retry import run_fixture_scenarios
from coursekit.io import check_name


def choose_bundle(bundle_path=None):
    # TODO D21-08-B01: 05에서 고정한 A/B 입력을 재사용하고 실행에 사용할 버전을 확인하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 05 outputs/dev_01/frozen_bundle.json을 선택적으로 지정. 원문을 바꾸지 않습니다.
    # 핵심: 마지막 프로젝트는 기존 흐름을 다시 연결합니다. 새 API·DB·벡터 검색을 만들지 않습니다.
    # BEGIN D21-08-B01

    # 1) --bundle 인자가 없으면 기본 체크포인트 번들을 생성하고, 지정되었으면 해당 JSON 파일을 그대로 읽어옴
    if bundle_path is None:
        bundle = make_bundle()  # 앞 교시 미완성자를 위한 제공 체크포인트
        print("[독립 시작점] 실제 D 실험을 개선한 결과가 아닙니다.")
    else:
        bundle = read_json(bundle_path)

    # 2) 번들 무결성 확인: 지식 버전, 스키마 버전, 그리고 비교할 A/B 프롬프트 버전이 모두 존재하는지 검증
    assert "context_version" in bundle and "schema_version" in bundle
    assert "A" in bundle.get("variants", {}) and "B" in bundle.get("variants", {})
    # H 결과를 보고 이 파일을 덮어쓰지 마세요.
    # END D21-08-B01
    return bundle


def choose_cases():
    # TODO D21-08-B02: 최종 확인용 H01~H03만 골라 세 질문의 A/B 계획을 만드세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: A/B 각 3질문, 첫 응답 총 6개. H03의 세 근거를 임의로 줄이지 않습니다.
    # BEGIN D21-08-B02

    # 1) 최종 확인용 Holdout 데이터셋(holdout_v1.json) 로드
    cases = read_json(DATA / "holdout_v1.json")
    expected_ids = ["H01", "H02", "H03"]

    # 2) 질문 ID 목록이 정확히 H01, H02, H03 순서인지, 각 케이스에 선택된 지식 ID(selected_ids)가 있는지 확인
    assert [c["case_id"] for c in cases] == expected_ids
    assert all(len(c.get("selected_ids", [])) >= 1 for c in cases)
    # H03은 세 근거(101, 102, 103)를 모두 사용하는 케이스이므로 임의로 줄이지 않음
    assert cases[2]["selected_ids"] == [101, 102, 103]
    # END D21-08-B02
    return cases


def make_report(rows):
    # TODO D21-08-B03: 검증과 사람 평가를 합치되 미실행·미평가 상태를 그대로 남기세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 정상·부족·형식 실패·참조 실패·사람 평가를 구분하고 B의 승리를 강요하지 않습니다.
    # BEGIN D21-08-B03

    # 1) 기본 요약 지표 생성 후, 첫 번째 시도(attempt == 1) 행만 추출 (H01~H03 × A/B = 총 6개)
    report = summarize(rows)
    first = [r for r in rows if r.get("attempt") == 1]

    # 2) 전체 시도 중 최대 attempt 횟수 계산 (행이 비어 있을 때를 대비해 default=0 설정)
    max_attempt = max((r.get("attempt", 0) for r in rows), default=0)

    # 3) 프로젝트 종합 메타데이터 기록: 미실행(not_run)과 사람 미평가(evidence_ok is None) 건수를 투명하게 보존
    report["project"] = {
        "name": "AI 지식 답변 생성기 v1",
        "first_target": len(first),
        "not_run": sum(1 for r in first if r.get("execution_state") == "not_run"),
        "human_pending": sum(1 for r in first if r.get("evidence_ok") is None),
        "max_attempt": max_attempt,
        "completion": "실제 관찰과 근거 대조 필요",
    }

    # 4) 제한된 재시도 원칙(최대 2회 이하)을 지켰는지 최종 검증
    assert max_attempt <= 2
    # END D21-08-B03
    return report


def choose_repeats():
    return 1


def main():
    import argparse

    parser = argparse.ArgumentParser(description="모델 호출 없이 Prompt 준비 또는 실제 수동 응답 검토")
    parser.add_argument("command", choices=["prepare", "review", "fixtures"], nargs="?", default="prepare")
    parser.add_argument("--run", default="holdout_01", help="영문 실험 폴더명; 기존 실험 덮어쓰기 금지")
    parser.add_argument("--bundle", type=Path, help="05에서 고정한 frozen_bundle.json. 미지정 시 제공 독립 시작점 사용")
    args = parser.parse_args()
    check_name(args.run)
    folder = HERE / "outputs" / args.run
    if args.command == "prepare":
        bundle = choose_bundle(args.bundle)
        cases = choose_cases()
        repeats = choose_repeats()
        prepare_experiment(folder, bundle, cases, repeats=repeats)
        print("[준비]", folder)
        print("prompts의 원문을 각각 새 대화에 입력하세요. 아직 실제 응답은 0개입니다.")
    elif args.command == "review":
        rows = review_experiment(folder)
        report = make_report(rows)
        write_summary(folder, report)
        print("[검토]", folder / "summary.md")
        print("raw가 없는 항목은 미실행, 사람 평가 null은 미평가입니다.")
    else:
        results = run_fixture_scenarios(read_json(DATA / "validation_fixtures.json"))
        write_json(HERE / "outputs" / "fixture_checks.json", {"source_mode": "fixture", "results": results})
        print("[샘플 검사] 호출 수 2·2·1·1. 모델의 실제 복구율이 아닙니다.")


if __name__ == "__main__":
    run(main)