/*
==============================================================================
[실습 보고서: 06_constraints.sql - DB 제약조건(CHECK·FK) 위반 검증 및 ROLLBACK 회복]
1. 실험 목적: FastAPI를 거치지 않고 DB에 직접 잘못된 데이터(빈 문자열 본문, 존재하지 않는 분류 ID)를
              INSERT 했을 때 DB 제약조건이 이를 차단하는지 확인하고, ROLLBACK으로 회복 후 기존 데이터 보존을 검증함.
2. 핵심 포인트:
   - CHECK 제약 위반 (SQLSTATE 23514): 본문(content)에 빈 문자열('')을 넣으면 NULL은 아니지만
     char_length(content) BETWEEN 1 AND 2000 규칙에 걸려 거부됨.
   - FOREIGN KEY 제약 위반 (SQLSTATE 23503): 부모 테이블(categories)에 없는 ID(-1)를 참조하려 하면 거부됨.
   - 오류 후 회복(25P02 방지): PostgreSQL은 BEGIN 블록 안에서 오류가 나면 해당 트랜잭션이 중단 상태가 되므로,
     반드시 ROLLBACK을 별도 실행해 정리해야 다음 SQL을 정상 실행할 수 있음.
==============================================================================
*/
-- Day18 | 실습 06: 제약조건·실패·회복 | PPT 42~47 | 35분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.

-- @step E6_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
DO $guard$
BEGIN
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database();
  END IF;
END;
$guard$;
SET search_path TO public;

-- @step E6_BEFORE expect=00000 capture=- reconnect=false
-- [실패 실험 전 상태 확인] 기존 지식 3건과 분류 3건의 초기 상태를 먼저 확인
SELECT id, title, content, category_id FROM public.knowledge ORDER BY id;

-- @step E6_PARENT expect=00000 capture=- reconnect=false
SELECT id,name FROM public.categories ORDER BY id;
SELECT id FROM public.categories WHERE id=-1;

-- @step E6_CHECK_BEGIN expect=00000 capture=- reconnect=false
BEGIN;

-- @step E6_BAD_CONTENT expect=23514 capture=- reconnect=false
-- [의도적 실패 1: 길이 CHECK 위반(23514)] 본문에 빈 문자열('')을 넣어 knowledge_content_length 제약 위반 유도
INSERT INTO public.knowledge(title,content,category_id) VALUES ('오류 확인','',1);

-- @step E6_CHECK_CANCEL expect=00000 capture=- reconnect=false
-- BEGIN TASK B06_01
-- TODO B06_01
-- 앞의 빈 본문 INSERT가 CHECK 오류로 거부된 뒤 이 구간만 따로 실행해 미확정 거래를 취소하세요.
-- [핵심 구현: 오류로 인해 중단 상태에 빠진 현재 트랜잭션을 ROLLBACK으로 취소하여 정상 상태로 회복]
ROLLBACK;
-- END TASK B06_01

-- @step E6_FK_BEGIN expect=00000 capture=- reconnect=false
BEGIN;

-- @step E6_BAD_FK expect=23503 capture=- reconnect=false
-- [의도적 실패 2: 외래키 FK 위반(23503)] 부모 categories에 존재하지 않는 분류 ID(-1)를 넣어 참조 무결성 위반 유도
INSERT INTO public.knowledge(title,content,category_id) VALUES ('오류 확인','정상 본문',-1);

-- @step E6_FK_CANCEL expect=00000 capture=- reconnect=false
-- [오류 후 회복] FK 오류 발생 후 이 줄만 단독 선택 실행하여 트랜잭션 정리
ROLLBACK;

-- @step E6_AFTER expect=00000 capture=- reconnect=false
-- [기존 데이터 보존 검증] 두 번의 INSERT 실패와 ROLLBACK 이후에도 기존 지식 3건과 분류 3건이 온전히 보존되었는지 확인
SELECT id, title, content, category_id FROM public.knowledge ORDER BY id;
SELECT id,name FROM public.categories ORDER BY id;