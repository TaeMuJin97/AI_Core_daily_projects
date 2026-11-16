"""
==============================================================================
[실습 보고서: Day 21 실습 01 - Prompt 구조와 요구사항 (01_prompt_structure/main.py)]
1. 실험 목적: 막연한 요청 대신 6요소(역할·작업·입력·제약·실패·출력)로 요구사항을 구조화하고,
              string.Template을 사용해 고정 규칙과 동적 변수(question, context_json)를 분리 조립함.
2. 핵심 포인트:
   - 6요소 정의 (D21-01-B01): role, task, input, constraints, failure, output 6개 키를 명확히 채움.
   - 안전한 템플릿 대입 (D21-01-B02): JSON의 중괄호({ })와 충돌하지 않도록 $변수 기반 Template을 쓰고,
     rows를 json.dumps(rows, ensure_ascii=False)로 직렬화하여 대입함.
   - 산출물 검증 및 저장 (D21-01-B03): 완성된 prompt 문자열에 질문과 지식 원문('개인 폴더')이
     정상 포함되었는지 assert로 확인하고 outputs/ 폴더에 requirements.json과 prompt.txt를 기록함.
==============================================================================
"""
"""Day21 실습 01: Prompt 구조와 요구사항. 실행: python main.py"""
from pathlib import Path
import sys
import json
from string import Template

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, write_text, run
from coursekit.prompting import CONTRACT_TEXT

# 기준: Day21 PPT 7~13장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.


def build_requirements():
    # TODO D21-01-B01: 역할·작업·입력·제약·실패·출력 여섯 칸을 완성하세요.
    # 입력·대상: PPT 8장의 여섯 요소
    # 완료 기준: 6개 키가 모두 있고 각 문장이 비어 있지 않습니다.
    # 핵심: 역할을 전문가로 꾸미는 것과 정확한 근거를 제공하는 것은 다릅니다.
    # BEGIN D21-01-B01
    requirements = {
        "role": "초보 수강생의 사내 교육·온보딩 도움말 작성자",  # 누구를 돕는 작성자인가?
        "task": "질문에 대해 한국어 2문장 이내로 명확하게 답하기",  # 어떤 질문에, 어떤 언어·길이로 답할까?
        "input": "사용자 질문과 선택한 지식 데이터 본문",  # 질문과 선택 지식
        "constraints": "반드시 제공한 지식 근거 범위에서만 답하고 예제 ID는 출처로 사용하지 않기",  # 근거 범위와 예제 ID 사용 금지
        "failure": "제공 자료에 없는 사실은 추측하지 말고 status를 insufficient_context로 두고 부족한 정보명을 기록하기",  # 없는 사실을 추측하지 않는 처리
        "output": "status, answer, source_ids, missing_information 네 필드를 가진 JSON 객체와 사용한 출처 ID",  # 출력할 네 필드 이름
    }
    # END D21-01-B01
    return requirements


def build_prompt(question, rows, requirements):
    # TODO D21-01-B02: Template에 질문·직렬화한 지식·출력 계약을 대입하세요.
    # 입력·대상: question, rows, requirements; CONTRACT_TEXT는 제공 코드
    # 완료 기준: 질문·지식 원문·네 필드 약속이 prompt에 있으며 $question이 남지 않습니다.
    # 핵심: 지식 본문은 데이터입니다. Template 대입은 코드 실행 또는 보안 권한 부여가 아닙니다.
    # BEGIN D21-01-B02
    # [핵심 구현 1: 전달받은 지식 목록(rows)을 한글이 깨지지 않게 JSON 문자열로 직렬화]
    context_json = json.dumps(rows, ensure_ascii=False)
    # JSON 중괄호와 충돌하지 않도록 $변수 형식인 Template을 사용합니다.
    template = Template(
        "[역할] $role\n[작업] $task\n[입력] $input\n[질문] $question\n[지식 데이터] $context_json\n[제약] $constraints\n[실패] $failure\n[출력] $contract"
    )
    # [핵심 구현 2: 6요소(**requirements)와 질문, 직렬화된 지식, 출력 계약(CONTRACT_TEXT) 대입]
    prompt = template.substitute(
        **requirements,
        question=question,
        context_json=context_json,
        contract=CONTRACT_TEXT,
    )
    # END D21-01-B02
    return prompt


def main():
    requirements = build_requirements()
    rows = read_json(DATA / "knowledge_v1.json")[:1]
    prompt = build_prompt("파일을 어디에 보관하나요?", rows, requirements)
    # TODO D21-01-B03: 요구사항과 Prompt 원문을 저장하고 기준 질문을 확인하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: outputs/requirements.json 및 prompt.txt 생성. 아직 실제 모델 품질 결과는 없습니다.
    # BEGIN D21-01-B03
    assert len(requirements) == 6
    assert all(isinstance(v, str) and v.strip() for v in requirements.values())
    # [핵심 구현 3: 완성된 prompt 안에 질문과 101번 지식 본문('개인 폴더')이 들어있는지 검증]
    assert "파일을 어디에 보관하나요?" in prompt
    assert "개인 폴더" in prompt
    assert "$question" not in prompt

    # [핵심 구현 4: outputs 폴더에 requirements.json과 prompt.txt 저장]
    write_json(HERE / "outputs" / "requirements.json", requirements)
    write_text(HERE / "outputs" / "prompt.txt", prompt)
    # END D21-01-B03
    print("[01] Prompt 요구사항과 원문 저장 완료. 모델 결과가 아닙니다.")


if __name__ == "__main__":
    run(main)