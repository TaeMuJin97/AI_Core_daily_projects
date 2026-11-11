/*
==============================================================================
[실습 보고서: 05_join.sql - JOIN을 통한 분류명 연결 및 LEFT JOIN / GROUP BY 집계]
1. 실험 목적: 정규화되어 두 테이블(categories, knowledge)로 나뉜 데이터를 JOIN으로 연결해
              어제(Day 17) API 응답처럼 분류명(category 문자열)을 함께 조회하고, 분류별 지식 수를 집계함[cite: 45, 59, 60, 62, 122].
2. 핵심 포인트:
   - INNER JOIN (JOIN): 양쪽 테이블에 모두 연결 데이터가 있는 행만 조회하므로, 지식이 있는 3건만 출력됨[cite: 60, 122].
   - LEFT JOIN과 GROUP BY: 지식이 아직 0건인 'reference' 분류도 결과 표에 남기기 위해
     부모(categories)를 왼쪽에 두고 LEFT JOIN을 수행함[cite: 61, 62, 122].
   - COUNT(*) vs COUNT(k.id): LEFT JOIN 시 지식이 없는 분류는 오른쪽(k.id)이 NULL이 되므로,
     COUNT(*)를 쓰면 1로 잘못 세어진다. 반드시 실제 자식 키인 COUNT(k.id)를 세어야 정확히 0이 나옴[cite: 62, 63, 122].
==============================================================================
*/
-- Day18 | 실습 05: JOIN·분류별 집계 | PPT 35~41, 74 | 35분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.

-- @step E5_GUARD expect=00000 capture=- reconnect=false
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

-- @step E5_JOIN expect=00000 capture=- reconnect=false
-- BEGIN TASK B05_01
-- TODO B05_01
-- 분류 PK와 지식 FK를 맞춰 분류명을 붙이세요. 결과 한 행은 지식 한 건이며 S0는 3행입니다.
-- [핵심 구현 1: 부모 PK(c.id)와 자식 FK(k.category_id)가 일치하는 조건(ON)으로 두 표를 연결해 분류명 표시]
SELECT k.id, k.title, c.name AS category
FROM public.knowledge AS k
JOIN public.categories AS c ON c.id = k.category_id
ORDER BY k.id;
-- END TASK B05_01

-- @step E5_GROUP expect=00000 capture=- reconnect=false
-- BEGIN TASK B05_02
-- TODO B05_02
-- 분류를 왼쪽에 두고 분류별 실제 지식 수를 세세요. 빈 reference 분류는 0이어야 합니다.
-- 힌트: NULL인 자식 ID를 세지 않는 COUNT를 사용합니다.
-- [핵심 구현 2: LEFT JOIN으로 빈 분류(reference)까지 보존하고, GROUP BY와 COUNT(k.id)로 실제 지식 수만 집계]
SELECT c.name AS category, COUNT(k.id) AS knowledge_count
FROM public.categories AS c
LEFT JOIN public.knowledge AS k ON k.category_id = c.id
GROUP BY c.id, c.name
ORDER BY c.id;
-- END TASK B05_02

-- @step E5_LENGTH expect=00000 capture=- reconnect=false
-- [전체 지식 통계 요약] 총 지식 건수(3건), 본문 글자 수 합계(64자), 최소 길이(20자), 최대 길이(24자) 집계
SELECT COUNT(*) AS knowledge_count,SUM(char_length(content)) AS total_chars,
MIN(char_length(content)) AS min_chars,MAX(char_length(content)) AS max_chars FROM public.knowledge;