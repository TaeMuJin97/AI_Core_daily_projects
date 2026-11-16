"""
==============================================================================
[실습 보고서: Day 21 실습 02 - Zero/Few-shot 예제 설계 및 버전 관리 (02_examples_versions/main.py)]
1. 실험 목적: 현재 지식(101~103)과 분리된 예제 전용 ID(901)를 사용해 정상 응답(answered)과
              정보 부족(insufficient_context) Few-shot 예제 쌍을 구성하고, 버전 및 실험 조건을 기록함.
2. 핵심 포인트:
   - 독립된 Few-shot 예제 설계 (D21-02-B01): 평가 질문(D/H)이나 실제 지식 ID(101~103)가 오염되지 않도록
     예제 전용 ID 901을 사용하여 정상 인용([901])과 정보 부족([], '대여료') 두 가지 처리 기준을 보여줌.
   - Zero-shot vs Few-shot 조립 (D21-02-B02): 동일 질문(case)과 동일 규칙("A") 위에서
     examples=[]와 examples=examples로 두 번들을 생성하고 901 포함 여부를 assert로 검증함.
   - 버전 및 통제 조건 기록 (D21-02-B03): 바꾼 요소(changed), 가설(hypothesis), 고정 조건(fixed)을
     명시하여 outputs/ 폴더에 저장함.
==============================================================================
"""
"""Day21 실습 02: Zero/Few-shot·버전. 실행: python main.py"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, write_text, run
from coursekit.prompting import make_bundle

# 기준: Day21 PPT 14~20장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.
from coursekit.prompting import render_prompt


def build_examples():
    # TODO D21-02-B01: 예제 ID 901을 사용해 정상 답과 정보 부족 답을 완성하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 정상·부족 예제 2개. 평가 질문 D/H를 Few-shot에 사용하지 않습니다.
    # 핵심: 입력 예제를 늘려도 모델 가중치가 바뀌는 것은 아닙니다.
    # BEGIN D21-02-B01
    example_context = [{"id": 901, "content": "대여 장소는 안내 데스크입니다."}]
    examples = [
        {
            "question": "어디서 대여하나요?",
            "context": example_context,
            "answer": {
                "status": "answered",
                "answer": "대여 장소는 안내 데스크입니다.",
                "source_ids": [901],
                "missing_information": "",
            },
        },
        {
            "question": "대여료는 얼마인가요?",
            "context": example_context,
            "answer": {
                "status": "insufficient_context",
                "answer": "제공된 지식에 대여료 정보가 없어 답할 수 없습니다.",
                "source_ids": [],
                "missing_information": "대여료",
            },
        },
    ]
    # END D21-02-B01
    return examples


def main():
    examples = build_examples()
    # TODO D21-02-B02: 같은 질문에 Zero-shot과 Few-shot Prompt를 각각 만드세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 두 Prompt가 생성됩니다. 이는 05의 근거 규칙 A/B와 별도 설계 실험입니다.
    # BEGIN D21-02-B02
    case = read_json(DATA / "dev_v1.json")[0]
    zero_bundle = make_bundle(examples=[])          # 예제 없는 입력 (Zero-shot)
    few_bundle = make_bundle(examples=examples)     # 작성한 예제 2개 포함 (Few-shot)
    zero_prompt, _ = render_prompt(zero_bundle, case, "A")
    few_prompt, _ = render_prompt(few_bundle, case, "A")

    # 예제 ID 901이 Zero-shot에는 없고 Few-shot에만 포함되었는지 검증
    assert "901" not in zero_prompt
    assert "901" in few_prompt
    # END D21-02-B02

    # TODO D21-02-B03: 변경점·가설·고정 조건과 두 Prompt를 저장하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 가설을 실제 성능 결과처럼 기록하지 않습니다.
    # BEGIN D21-02-B03
    experiment = {
        "experiment": "examples_design_only",
        "base_version": "examples_zero_v1",
        "new_version": "examples_few_v1",
        "changed": "예제 ID 901 기반 정상 응답(answered) 및 정보 부족(insufficient_context) Few-shot 예제 2개 추가",
        "hypothesis": "예제를 통해 JSON 출력 형식 준수율과 근거 부족 시 추측 방지 기준이 더 명확해질 것이다",
        "fixed": [
            "question(D01)",
            "context_version(knowledge_v1)",
            "schema_version(answer_schema_v1)",
            "variant(A)",
        ],
        "source_mode": "design_only",
    }
    write_json(HERE / "outputs" / "examples.json", examples)
    write_json(HERE / "outputs" / "experiment.json", experiment)
    write_text(HERE / "outputs" / "zero_prompt.txt", zero_prompt)
    write_text(HERE / "outputs" / "few_prompt.txt", few_prompt)
    # END D21-02-B03
    print("[02] 예제·버전 설계 완료. 05는 예제 고정, 근거 규칙만 비교합니다.")


if __name__ == "__main__":
    run(main)