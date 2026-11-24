"""Day27 강의 실습. 실행은 역할 폴더에서 Python으로 실행합니다."""
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# 1. 경로 설정: 어느 터미널 위치에서 실행해도 상위 폴더의 coursekit을 import하도록 고정
# -----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROLE_ROOT = next(p for p in HERE.parents if (p / "coursekit").is_dir())
sys.path.insert(0, str(ROLE_ROOT))

import argparse
from fastapi import FastAPI, HTTPException
from coursekit.api import RagRequest          # 입력 JSON 계약(candidate_k 1..20 등 자동 검증)
from coursekit.pipeline import StageError     # 파이프라인 Stage별 격리 예외
from coursekit.runtime import create_demo_chain
from coursekit.workshops import STAGE_RUNNERS
from coursekit.io import save_report

# -----------------------------------------------------------------------------
# 2. 서버 측 고정 권한 상수 (클라이언트 입력의 role 문자열을 신뢰하지 않음)
# -----------------------------------------------------------------------------
SERVER_TRUSTED_ROLE = "learner"


def make_service_chain(offline: bool):
    """Rewrite → Retrieve → Rerank → Context → Generation·Validation을 연결합니다."""
    # BEGIN D27-08-B01
    # [흐름 이해: 실행 모드(offline vs live)에 맞는 전체 RAG Runnable 파이프라인 생성]
    # - offline=True : 외부 API·GPU·DB 호출 없이 고정 Fixture 부품으로 조립
    # - offline=False: CUDA GPU E5 + PostgreSQL(d27_rag) + GPU Cross-Encoder + LLM API로 조립
    return create_demo_chain(offline=bool(offline))
    # END D27-08-B01


def wire_fastapi(chain) -> FastAPI:
    """API 요청의 role 문자열을 신뢰하지 않고 서버에서 learner 역할을 지정합니다."""
    # BEGIN D27-08-B02
    # [흐름 이해: FastAPI 라우터와 RAG Runnable 연결 + 오류 상태 코드 분리]
    # 1) 엔드포인트 경로는 workshops.py / README.md 계약대로 POST /api/v1/rag/answer 사용
    # 2) 파라미터 타입을 RagRequest(Pydantic)로 선언하면 candidate_k=0 같은 잘못된 입력은
    #    chain.invoke()가 실행되기도 전에 FastAPI가 자동으로 HTTP 422를 반환합니다.
    # 3) 권한(trusted_role)은 요청 JSON을 신뢰하지 않고 서버에서 직접 "learner"를 주입합니다.
    # 4) StageError나 내부 예외는 '정보 부족(200)'으로 위장하지 않고 HTTP 502로 반환하며,
    #    민감한 예외 원문(DB 비밀번호·API 키 등)은 응답에 노출하지 않습니다.
    app = FastAPI(title="Day27 Enhanced RAG API")

    @app.post("/api/v1/rag/answer")
    def answer_endpoint(req: RagRequest):
        # 검증된 요청 dict에 서버가 보증하는 trusted_role을 명시적으로 덮어씌웁니다.
        payload = {
            **req.model_dump(),
            "trusted_role": SERVER_TRUSTED_ROLE,
        }
        try:
            return chain.invoke(payload)
        except ValueError as exc:
            # 입력 값 범위 등 클라이언트 요청 오류는 422로 반환
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except StageError as exc:
            # 파이프라인 내부 단계 실패는 stage와 code만 안전하게 담아 502로 반환
            raise HTTPException(
                status_code=502,
                detail={"error": "stage_error", "stage": exc.stage, "code": exc.code},
            ) from exc
        except Exception as exc:
            # 예상치 못한 서버/외부 연동 오류는 내부 원문을 숨기고 502로 반환
            raise HTTPException(
                status_code=502,
                detail={"error": "internal_rag_error", "message": "RAG 처리 실패"},
            ) from exc

    return app
    # END D27-08-B02


def main():
    parser = argparse.ArgumentParser(description="Day27 실습 08 · 08_enhanced_rag_api")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="교육용 고정 데이터·점수. 모델 품질 실측이 아닙니다.",
    )
    args = parser.parse_args()

    report = STAGE_RUNNERS[8](args.offline, [make_service_chain, wire_fastapi])
    path = save_report(
        HERE,
        "day27_08_" + ("fixture" if args.offline else "live") + ".json",
        report,
    )
    print("실습 08 결과:", path)
    print("보고서를 확인하고 reports/review.md에 원문 대조·실행 모드를 기록하세요.")


if __name__ == "__main__":
    main()