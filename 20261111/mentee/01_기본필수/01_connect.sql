/*
==============================================================================
[실습 보고서: 01_connect.sql - PostgreSQL 서버 접속 확인 및 현재 DB 검증]
1. 실험 목적: pgAdmin Query Tool이 로컬 PostgreSQL 서버의 개인 학습용 DB(knowledge_lab)에
              정확히 연결되었는지 SQL 함수로 검증함.
2. 핵심 포인트:
   - 단순 연결(SELECT 1)과 작업 공간(current_database()) 분리 확인: 서버 연결이 성공했더라도
     기본 DB(postgres)에 잘못 접속해 있을 수 있으므로 반드시 DB 이름을 함께 확인함.
   - 클라이언트/서버 인코딩 확인: 한글 데이터('한글 연결 확인')가 깨지지 않고 입출력되는지 점검함.
==============================================================================
*/
-- Day18 | 실습 01: 접속과 첫 SQL | PPT 7~13, 68, 78~80 | 30분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.

-- @step E1_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
-- 개인 수업용 DB에서만 실행합니다. 이름만 맞다고 운영 DB가 안전해지는 것은 아닙니다.
DO $guard$
BEGIN
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database();
  END IF;
END;
$guard$;
SET search_path TO public;

-- @step E1_PING expect=00000 capture=- reconnect=false
-- [연결 생존 확인] 테이블을 읽지 않고 서버가 쿼리에 정상 응답(1)하는지 빠르게 테스트
SELECT 1 AS connected;

-- @step E1_DB expect=00000 capture=- reconnect=false
-- BEGIN TASK B01_01
-- 해설 B01_01
-- current_database()는 현재 연결이 사용하는 DB를 보여줍니다.
-- SELECT 1만 성공해도 다른 DB에 연결했을 수 있으므로 두 결과를 함께 확인합니다.
-- [핵심 구현: 현재 접속 중인 데이터베이스 이름이 'knowledge_lab'인지 검증]
SELECT current_database() AS database_name;
-- END TASK B01_01

-- @step E1_INFO expect=00000 capture=- reconnect=false
-- [접속 계정 및 서버 버전 확인] 현재 사용자(postgres)와 PostgreSQL 18 엔진 버전 조회
SELECT current_user AS user_name, version() AS server_version;

-- @step E1_ENCODING expect=00000 capture=- reconnect=false
-- [인코딩 및 한글 입출력 확인] UTF8 환경에서 한글 문자열이 정상 반환되는지 확인
SHOW client_encoding;
SELECT '한글 연결 확인' AS korean_text;