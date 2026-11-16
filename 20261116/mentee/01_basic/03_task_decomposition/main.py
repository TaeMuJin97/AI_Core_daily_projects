"""
==============================================================================
[실습 보고서: Day 21 실습 03 - 작업 분해와 정보 부족 판단 (03_task_decomposition/main.py)]
1. 실험 목적: 큰 질문을 '요구 사실 파악 -> 근거 대조 -> 상태 결정 -> 외부 검사'로 분해하고,
              질문이 요구하는 사실 중 하나라도 근거가 부족하면 추측 없이 insufficient_context로 처리함.
2. 핵심 포인트:
   - 요구 사실 vs 지원 근거 대조 (D21-03-B01): card["required"]의 각 사실이 card["supported"]에
     유효한 출처 ID와 함께 존재하는지 확인하고, 없으면 missing 리스트에 추가함.
   - 일관된 상태 정책 적용 (D21-03-B02): missing 또는 conflicts가 하나라도 존재하면 부분 답변을 섞지 않고
     status="insufficient_context", source_ids=[]로 결정하며, 모두 충족될 때만 answered와 출처 ID를 반환함.
   - 관찰 가능한 결과 지시문 (D21-03-B03): 긴 내부 사고(CoT) 전체 공개를 요구하는 대신,
     질문 요구 사실 확인·근거 대조·정보 부족 처리·최종 4필드 JSON 반환을 명확히 지시함.
==============================================================================
"""
"""Day21 실습 03: 작업 분해와 정보 부족. 실행: python main.py"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROLE_ROOT = HERE.parents[1]
sys.path.insert(0, str(ROLE_ROOT))
from coursekit.io import DATA, read_json, write_json, write_text, run

# 기준: Day21 PPT 21~27장. 실제 모델 호출/실습 데이터 수정은 하지 않습니다.
# outputs는 실행 시 생성됩니다. 05/08의 모델 응답은 직접 수집한 원문만 등록합니다.


def analyze_card(card):
    # TODO D21-03-B01: 질문이 요구하는 사실과, 제공 자료가 지원하는 사실을 구분하세요.
    # 입력·대상: 교사가 작성한 required/supported/conflicts 카드
    # 완료 기준: C01 missing=[], C02 missing=[보관 기간]
    # 핵심: 이 코드는 자유로운 질문의 의미를 자동 이해하지 않습니다. 명시된 판단 카드를 처리합니다.
    # BEGIN D21-03-B01
    required = list(card["required"])
    supported = dict(card["supported"])
    missing = []
    for fact in required:
        # supported에 해당 fact 키가 없거나 연결된 출처 ID 목록이 비어 있으면 부족한 사실로 분류
        if fact not in supported or not supported[fact]:
            missing.append(fact)
    conflicts = list(card.get("conflicts", []))
    # END D21-03-B01

    # TODO D21-03-B02: 하나라도 근거가 부족하면 수업의 정보 부족 상태를 선택하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: README의 예상 결과와 출력 파일을 대조합니다.
    # 핵심: 오늘 계약은 부분 답변을 새 상태로 추가하지 않습니다. 충분한 근거가 없으면 명시적으로 멈춥니다.
    # BEGIN D21-03-B02
    status = "insufficient_context" if (missing or conflicts) else "answered"

    # 중요한 부분(source_ids): answered 상태일 때만 지원된 출처 ID를 순서대로 수집(중복 제거)
    source_ids = []
    if status == "answered":
        for fact in required:
            for sid in supported[fact]:
                if sid not in source_ids:
                    source_ids.append(sid)

    result = {
        "case_id": card["case_id"],
        "required": required,
        "missing": missing,
        "conflicts": conflicts,
        "status": status,
        "source_ids": source_ids,
        "basis": "teacher_authored_fact_card",
    }
    # END D21-03-B02
    return result


def main():
    cards = read_json(DATA / "decomposition_cards.json")
    # TODO D21-03-B03: 정상·정보 부족의 판단과 최종 출력 지시를 저장하세요.
    # 입력·대상: 아래 함수 인자와 제공 데이터만 사용합니다.
    # 완료 기준: 2개 결과와 작업 지시를 저장합니다. 모델 추론 관찰 기록이 아닙니다.
    # BEGIN D21-03-B03
    results = []
    for card in cards[:2]:
        results.append(analyze_card(card))

    # 검증: C01은 정상 답변 가능(missing=[]), C02는 보관 기간 정보 부족(missing=["보관 기간"])
    assert results[0]["missing"] == [] and results[0]["status"] == "answered"
    assert "보관 기간" in results[1]["missing"] and results[1]["status"] == "insufficient_context"

    instruction = (
        "[작업]\n"
        "질문이 요구하는 사실을 확인하세요.\n"
        "제공된 지식이 그 사실을 뒷받침하는지 대조하세요.\n\n"
        "[답변 기준]\n"
        "자료로 답할 수 있으면 답과 출처 ID를 반환하세요.\n"
        "부족하면 추측하지 말고 status를 insufficient_context로 두고 필요한 정보를 적으세요.\n\n"
        "[출력]\n"
        "내부 사고 기록 대신 최종 JSON만 반환하세요.\n"
        "필드: status, answer, source_ids, missing_information"
    )
    write_json(HERE / "outputs" / "task_cards.json", results)
    write_text(HERE / "outputs" / "task_instruction.txt", instruction)
    # END D21-03-B03
    print("[03] 판단 카드 완료. 근거 대조는 사람의 판단이 포함됩니다.")


if __name__ == "__main__":
    run(main)