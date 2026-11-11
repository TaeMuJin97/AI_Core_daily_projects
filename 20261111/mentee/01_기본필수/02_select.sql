/*
==============================================================================
[실습 보고서: 02_select.sql - 지식 데이터 SELECT 조회·WHERE 조건 필터링·ORDER BY 정렬]
1. 실험 목적: 초기 기준 데이터(S0, 지식 3건)를 대상으로 필요한 열(Column)만 선택하고,
              특정 ID나 분류 조건(WHERE) 및 정렬 기준(ORDER BY)을 적용해 원하는 행(Row)을 조회함.
2. 핵심 포인트:
   - 논리적 읽기 순서: FROM(어느 테이블) -> WHERE(어떤 조건) -> SELECT(어떤 열) -> ORDER BY(어떤 순서).
   - 0행(Empty Result)과 SQL 오류의 구분: 존재하지 않는 ID(id = -1)를 조회하면 에러가 발생하는 것이 아니라
     '0행(No rows)'이라는 정상 결과가 반환됨 (이를 HTTP 404로 바꾸는 것은 내일 연결할 FastAPI의 역할).
==============================================================================
*/
-- Day18 | 실습 02: 지식 SELECT·조건·정렬 | PPT 14~20 | 35분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)

-- @step E2_GUARD expect=00000 capture=- reconnect=false
-- 제공된 안전 확인입니다. 이 블록은 TODO가 아닙니다.
DO $guard$
BEGIN
  IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN
    RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database();
  END IF;
END;
$guard$;
SET search_path TO public;

-- @step E2_LIST expect=00000 capture=- reconnect=false
-- BEGIN TASK B02_01
-- TODO B02_01
-- 지식 표에서 id·title·category_id를 조회하세요. ID 오름차순으로 세 지식이 보여야 합니다.
-- [핵심 구현 1: public.knowledge 테이블에서 3개 열을 ID 오름차순(1, 2, 3)으로 전체 조회]
SELECT id, title, category_id FROM public.knowledge ORDER BY id;
-- END TASK B02_01

-- @step E2_DETAIL expect=00000 capture=- reconnect=false
-- BEGIN TASK B02_02
-- TODO B02_02
-- WHERE를 넣어 S0의 서버 실행 지식(id=2) 한 건만 조회하세요. 실행 전 실제 ID를 확인합니다.
-- [핵심 구현 2: WHERE 절을 사용하여 고유 식별자(id = 2, '서버 실행') 단건 상세 조회]
SELECT id, title, content FROM public.knowledge
WHERE id = 2;
-- END TASK B02_02

-- @step E2_CATEGORY expect=00000 capture=- reconnect=false
-- BEGIN TASK B02_03
-- TODO B02_03
-- 분류 1의 지식을 ID 오름차순으로 조회하세요. S0에서는 id 1·3 두 행입니다.
-- [핵심 구현 3: category_id가 1(learning)인 행만 필터링한 뒤 ORDER BY로 정렬하여 조회]
SELECT id, title FROM public.knowledge
WHERE category_id = 1
ORDER BY id;
-- END TASK B02_03

-- @step E2_EMPTY expect=00000 capture=- reconnect=false
-- [빈 결과 확인] 없는 ID(-1) 조회 시 SQL 에러가 아닌 정상 0행(0 rows)이 반환됨을 확인
SELECT id, title FROM public.knowledge WHERE id=-1;