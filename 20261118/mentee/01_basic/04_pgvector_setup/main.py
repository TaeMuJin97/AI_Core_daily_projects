"""
==============================================================================
[실습 보고서: Day 23 실습 04 - PostgreSQL 18.6 서버 확장(pgvector) 및 Python 연결 검증 (main.py)]
1. 실험 목적:
   - Windows 11 로컬 환경의 PostgreSQL 18.6 서버에 C++로 빌드·배치한 pgvector 확장(v0.8.7)이
     정상적으로 인식 및 활성화되었는지 SQL 프로브(Probe) 쿼리와 Python(psycopg) 연동으로 검증함.
2. 핵심 아키텍처 개념 (4단계 계층 분리):
   - 1계층 (서버 바이너리 배치): C:\Program Files\PostgreSQL\18\lib\vector.dll 및
     share\extension\vector.control 파일이 존재해야 pg_available_extensions 뷰에 나타남.
   - 2계층 (DB 단위 활성화): 서버에 파일이 있어도 각 데이터베이스마다 'CREATE EXTENSION vector;'를
     실행해야 installed_version이 채워지고 ::vector 타입과 <=> 연산자를 쓸 수 있음.
   - 3계층 (수학적 연산자 프로브): 무거운 384차원 E5 모델을 돌리기 전에, 3차원 직교 벡터
     '[1,0,0]'과 '[0,1,0]'의 코사인 거리(<=>)가 정확히 1.0(1 - cos 90°)으로 계산되는지 분리 검증함.
   - 4계층 (Python 커넥션 어댑터): pip install pgvector 및 연결 시마다 register_vector(conn)를
     호출하여 Python 리스트/NumPy 배열과 PostgreSQL vector 타입을 양방향 매핑함.
==============================================================================
"""
"""Day23 실습 04 · 서버 확장과 Python 연결 (기본필수, mentee).

실행: python main.py --mode fixture
실제 E5/DB: python main.py --mode live  (필요한 선행 설치 후)
수강생 TODO: 3개 / 상세 요구사항은 각 함수의 주석 및 README.md.
fixture는 모의 시연이지 모델·PostgreSQL 실측 결과가 아닙니다.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))
from day23kit.mathops import cosine_distance
from day23kit.db import connect_db
from day23kit.io import save_result


# BEGIN D23-04-B01
def sql_server_info():
    """
    TODO D23-04-B01 · sql_server_info
        pgAdmin에서 실행할 서버 버전·현재 DB 조회 SQL을 작성하세요.
        반드시 SELECT version()과 current_database()를 포함하세요.
        DB 변경이나 DROP/CREATE DATABASE는 하지 않습니다.
    """
    # [핵심 포인트 1: 접속 중인 PostgreSQL 서버 버전 및 대상 데이터베이스 확인]
    # - pgvector 확장은 서버 전체가 아니라 '현재 접속한 DB(current_database())'에만 활성화됩니다.
    # - 따라서 작업 전 반드시 PostgreSQL 18.6 버전과 현재 연결된 DB 이름, 계정을 먼저 조회해야 합니다.
    # - 기존 DB나 테이블을 삭제/초기화(DROP/CREATE)하지 않는 안전한 읽기 전용 조회 쿼리입니다.
    return "SELECT version(); SELECT current_database(), current_user;"
# END D23-04-B01


# BEGIN D23-04-B02
def sql_extension_state():
    """
    TODO D23-04-B02 · sql_extension_state
        vector 확장의 제공 여부와 설치 여부를 확인하는 SQL 문자열을 작성하세요.
        pg_available_extensions, installed_version, WHERE name='vector' 사용.
    """
    # [핵심 포인트 2: 서버 확장 파일 존재 여부(default_version)와 DB 활성화 여부(installed_version) 분리 진단]
    # - pg_available_extensions 시스템 뷰에서 name='vector' 행이 조회되면:
    #   1) 행 자체가 존재함 (default_version 출력) -> nmake install로 서버 폴더에 파일 배치 성공
    #   2) installed_version이 NULL이 아님 (예: '0.8.7') -> 현재 DB에서 CREATE EXTENSION vector 활성화 완료
    #   3) 만약 installed_version이 NULL이면 서버 파일은 있으나 현재 DB에 아직 활성화하지 않은 상태임
    return "SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name='vector';"
# END D23-04-B02


# BEGIN D23-04-B03
def sql_distance_probe():
    """
    TODO D23-04-B03 · sql_distance_probe
        SQL에서 3차원 벡터 [1,0,0]과 [0,1,0]의 Cosine distance를 계산하세요.
        문자열 반환. CAST는 ::vector, 연산자는 <=>를 사용합니다.
        예상값 1.0이며 384차원 E5 출력이 아닙니다.
    """
    # [핵심 포인트 3: 3차원 기준 벡터를 이용한 pgvector 타입 캐스팅(::vector) 및 코사인 거리(<=>) 동작 검증]
    # - E5 모델(384차원)을 연결하기 전, DB 엔진 내부의 vector.dll 연산자가 정상 작동하는지 분리 테스트합니다.
    # - [1,0,0]과 [0,1,0]은 서로 수직(90도)이므로 내적=0, Cosine Similarity=0.0이며,
    #   pgvector의 Cosine Distance(<=>)는 (1 - Cosine Similarity) = 1 - 0.0 = 1.0을 반환해야 합니다.
    return "SELECT '[1,0,0]'::vector <=> '[0,1,0]'::vector AS cosine_distance;"
# END D23-04-B03


def run(mode, level, args):
    sqls = {
        "server": sql_server_info(),
        "extension": sql_extension_state(),
        "distance": sql_distance_probe(),
    }
    result = dict(
        exercise=4,
        level=level,
        source_mode="not_run" if mode == "fixture" else "pgvector_live",
        sql_for_pgadmin=sqls,
        db_check="not_run",
    )
    if level >= 2:
        result["illustrated_extension_state"] = check_extension_row(
            ("vector", "0.8.7", None)
        )
        result["example_error_stage"] = classify_install_error(
            "postgres.h not found"
        )
    if level >= 3:
        result["manual_pending"] = audit_install_steps({})
    if mode == "live":
        # live만 실제 DB 연결. Windows 빌드 및 CREATE EXTENSION은 사전 수동 절차.
        with connect_db(Path(__file__).with_name(".env")) as conn:
            ver = conn.execute("SELECT version()").fetchone()[0]
            dbname = conn.execute("SELECT current_database()").fetchone()[0]
            ext = conn.execute(
                "SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name='vector'"
            ).fetchone()
            result["db_check"] = (
                {
                    "server_version": ver,
                    "database": dbname,
                    "extension": check_extension_row(ext),
                }
                if level >= 2
                else {
                    "server_version": ver,
                    "database": dbname,
                    "extension_provided": ext is not None,
                }
            )
            if ext is not None and ext[2]:
                result["db_check"]["distance_probe"] = float(
                    conn.execute(sql_distance_probe()).fetchone()[0]
                )
            else:
                result["db_check"][
                    "distance_probe"
                ] = "not_run_extension_not_activated"
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Day23 실습 04 · 서버 확장과 Python 연결"
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="fixture=모의 벡터/오프라인, live=실제 E5/DB가 필요한 단계",
    )
    args = parser.parse_args()
    result = run(args.mode, 1, args)
    path = save_result(Path(__file__).resolve().parent, "exercise_04.json", result)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    print("결과 저장:", path)


if __name__ == "__main__":
    main()