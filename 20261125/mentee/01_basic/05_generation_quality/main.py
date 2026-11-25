"""Day28 실습 05 · 01_basic · 실행 진입점.
수강생은 TODO의 요구사항을 해결하고 예상 출력과 비교합니다.
강사용 코드에는 데이터 계약, 단계별 처리 의도와 예외를 주석으로 설명합니다.
"""
from pathlib import Path
import argparse
import sys

ROLE_ROOT = Path(__file__).resolve().parents[2]
if str(ROLE_ROOT) not in sys.path:
    sys.path.insert(0, str(ROLE_ROOT))

from coursekit.eval_workshops import execute
from coursekit.eval_report import write_json


def _format_claim_label(claim: dict, index: int) -> str:
    """Claim dict의 키 구조(id/claim_id/name, text/claim)에 관계없이 식별 이름과 내용을 조합합니다."""
    cid = claim.get("claim_id") or claim.get("id") or claim.get("name")
    text = claim.get("text") or claim.get("claim") or claim.get("statement")
    if cid and text:
        return f"{cid}({text})"
    if cid:
        return str(cid)
    if text:
        return str(text)
    return f"claim_{index}"


def claim_faithfulness(claims: list[dict]) -> float | None:
    """Claim 목록에서 근거가 지지하는 Claim 비율을 계산하세요. Claim이 없으면 None."""
    # TODO D28-05-B01
    # [흐름 이해: Claim-level Faithfulness = (Context가 지지하는 주장 수) / (전체 주장 수)]
    # 1) claims가 빈 목록이면 평가할 주장이 없으므로 1.0이 아니라 None(N/A)을 반환합니다.
    # 2) 각 claim dict의 'supported'(교육용 사람 레이블)가 True인 개수를 세어 비율(0.0 ~ 1.0)을 반환합니다.
    if not isinstance(claims, list):
        raise TypeError("claims는 dict 원소를 담은 list여야 합니다.")
    if not claims:
        return None

    supported_count = 0
    for item in claims:
        if not isinstance(item, dict) or "supported" not in item:
            raise ValueError(f"각 Claim에는 'supported' 키가 필요합니다: {item!r}")
        if bool(item["supported"]):
            supported_count += 1

    return supported_count / len(claims)


def describe_claim_result(claims: list[dict]) -> str:
    """비지원 Claim을 이름과 함께 기록하세요. “모든 Claim 지원”과 “Claim 없음”은 구별합니다."""
    # TODO D28-05-B02
    # [흐름 이해: 3가지 상태 명확히 구분]
    # 1) Claim 없음([]): 주장 0개이므로 Faithfulness=None이며 "모든 Claim 지원"과 구분
    # 2) 비지원 Claim 존재: supported가 False인 Claim들의 이름/내용을 모두 나열
    # 3) 모든 Claim 지원: 비지원 항목이 0건임을 명시 (단, Faithfulness는 Context 대조이며 Reference 정답성과 별개)
    if not isinstance(claims, list):
        raise TypeError("claims는 dict 원소를 담은 list여야 합니다.")
    if not claims:
        return "Claim 없음: 평가할 주장이 0개이므로 Faithfulness는 None(N/A)으로 처리합니다."

    unsupported_labels: list[str] = []
    for idx, item in enumerate(claims, start=1):
        if not isinstance(item, dict) or "supported" not in item:
            raise ValueError(f"각 Claim에는 'supported' 키가 필요합니다: {item!r}")
        if not bool(item["supported"]):
            unsupported_labels.append(_format_claim_label(item, idx))

    if not unsupported_labels:
        return (
            f"모든 Claim 지원 ({len(claims)}/{len(claims)}): "
            "모든 주장이 제공된 Context에서 확인되었습니다 (Reference Answer와의 정답성은 별도 평가)."
        )

    return (
        f"비지원 Claim {len(unsupported_labels)}건 발견: "
        + ", ".join(unsupported_labels)
        + " — 제공된 Context에서 지지되지 않습니다."
    )


def main():
    parser = argparse.ArgumentParser(description="Day28 RAG Evaluation 실습")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="고정 학습 데이터만 실행(기본값)")
    mode.add_argument(
        "--live",
        action="store_true",
        help="실제 CUDA GPU/DB/LLM 연결. 06~08만 지원하며 API 비용 발생 가능",
    )
    args = parser.parse_args()
    hooks = {
        "claim_faithfulness": claim_faithfulness,
        "describe_claim_result": describe_claim_result,
    }
    # 학생 과제 함수가 실제 서비스가 아니라 이 지도에 정의된 실습 단계에서 호출됩니다.
    try:
        result = execute(5, hooks, live=args.live, level="01_basic")
    except Exception as exc:
        # 실패 기록에는 Key·Password·원본 Prompt를 포함하지 않습니다.
        failure = {
            "status": "execution_failed",
            "exercise": 5,
            "stage": getattr(exc, "stage", "evaluation"),
            "error_type": type(exc).__name__,
            "mode": "live" if args.live else "offline_fixture",
        }
        write_json(Path(__file__).resolve().parent / "outputs" / "failure.json", failure)
        raise
    output = Path(__file__).resolve().parent / "outputs" / "result.json"
    write_json(output, result)
    # 학생이 코드로 만든 설명 보고서는 별도 Markdown 파일로 저장합니다.
    if isinstance(result.get("markdown_report"), str):
        (output.parent / "report.md").write_text(result["markdown_report"], encoding="utf-8")
    print("Day28 실습 5 · 01_basic ·", result["mode"])
    print("출력:", output)
    return result


if __name__ == "__main__":
    main()