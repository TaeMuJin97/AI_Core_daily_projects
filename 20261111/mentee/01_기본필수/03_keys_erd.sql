/*
==============================================================================
[실습 보고서: 03_keys_erd.sql - 부모·자식 두 테이블의 PK/FK 관계 및 DDL 트랜잭션 연습]
1. 실험 목적: 본 테이블(categories, knowledge)을 건드리지 않고, 트랜잭션(BEGIN ~ ROLLBACK) 안에서
              연습용 테이블(_try)을 생성하며 PRIMARY KEY(기본키)와 REFERENCES(외래키 참조)를 구현함.
2. 핵심 포인트:
   - 부모(1) 대 자식(0..N) 관계: 분류(categories_try)가 먼저 존재해야 자식 지식(knowledge_try)이
     그 분류의 id를 참조(REFERENCES)할 수 있음.
   - 안전한 DDL 연습: BEGIN 블록 안에서 테이블을 만들고 조회한 뒤 ROLLBACK을 실행하면,
     PostgreSQL에서는 CREATE TABLE 자체도 완전히 취소되어 연습용 테이블이 깔끔하게 사라짐(true/true).
==============================================================================
*/
-- Day18 | 실습 03: 두 테이블·키·ERD | PPT 21~28, 69~70, 73 | 30분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)

-- @step E3_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
DO $guard$
BEGIN
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database();
  END IF;
END;
$guard$;
SET search_path TO public;

-- @step E3_BEGIN expect=00000 capture=- reconnect=false
-- [트랜잭션 시작] 연습용 테이블이 영구 반영되지 않도록 취소 가능한 작업 묶음 시작
BEGIN;

-- @step E3_CREATE expect=00000 capture=- reconnect=false
CREATE TABLE public.categories_try (
-- BEGIN TASK B03_01
-- TODO B03_01
-- 연습용 분류의 id를 행 식별 키로 선언하세요. IDENTITY 자동 발급은 이 축소 예제에서 사용하지 않습니다.
-- [핵심 구현 1: 부모 테이블의 각 행을 유일하게 식별하고 NULL을 금지하는 기본키(PRIMARY KEY) 선언]
id INTEGER PRIMARY KEY,
-- END TASK B03_01
name TEXT NOT NULL
);

CREATE TABLE public.knowledge_try (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
-- BEGIN TASK B03_02
-- TODO B03_02
-- category_id가 categories_try.id를 참조하게 하세요. 자식이 부모를 가리키는 방향입니다.
-- [핵심 구현 2: 자식 테이블의 category_id가 부모 테이블(categories_try)의 id만 가리키도록 외래키(REFERENCES) 연결]
category_id INTEGER NOT NULL
  REFERENCES public.categories_try(id)
-- END TASK B03_02
);

-- @step E3_SEED expect=00000 capture=- reconnect=false
-- [연습 데이터 입력] 부모 분류(1, '연습')를 먼저 넣고, 이를 참조하는 자식 지식(1, '안내', 1)을 입력
INSERT INTO public.categories_try VALUES (1,'연습');
INSERT INTO public.knowledge_try VALUES (1,'안내',1);

-- @step E3_READ expect=00000 capture=- reconnect=false
-- [생성 확인] 연습용 자식 테이블에 데이터가 정상 입력되었는지 조회
SELECT * FROM public.knowledge_try ORDER BY id;

-- @step E3_CANCEL expect=00000 capture=- reconnect=false
-- [트랜잭션 취소] 연습용 테이블 생성(CREATE)과 데이터 입력(INSERT)을 모두 취소하고 원상복구
ROLLBACK;

-- @step E3_GONE expect=00000 capture=- reconnect=false
-- [취소 검증] ROLLBACK 후 연습용 테이블 두 개가 모두 사라졌는지(NULL -> true, true) 확인
SELECT to_regclass('public.categories_try') IS NULL AS parent_gone,
       to_regclass('public.knowledge_try') IS NULL AS child_gone;