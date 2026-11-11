/*
==============================================================================
[실습 보고서: 04_crud.sql - SQL 기반 지식 CRUD(INSERT·UPDATE·DELETE) 및 RETURNING 검증]
1. 실험 목적: 트랜잭션(BEGIN ~ ROLLBACK) 보호 구간 안에서 지식 데이터의 추가(INSERT),
              수정(UPDATE), 삭제(DELETE) 구문을 완성하고 RETURNING으로 변경된 행을 즉시 확인함[cite: 54, 59, 122].
2. 핵심 포인트:
   - RETURNING 활용: 별도의 SELECT 없이도 INSERT 시 자동 발급된 ID나 UPDATE/DELETE 대상 행의 값을 즉시 반환받음[cite: 55, 56, 57].
   - 안전한 변경 절차(Safe Write): 변경 전 SELECT로 대상을 먼저 확인하고, BEGIN 안에서 실행한 뒤
     ROLLBACK으로 취소하여 초기 기준 데이터(S0, 3건)를 훼손 없이 그대로 유지함[cite: 54, 122].
   - 시퀀스(IDENTITY) 특성: INSERT를 ROLLBACK하여 행이 사라져도 한 번 발급된 번호는 되돌아가지 않을 수 있음.
==============================================================================
*/
-- Day18 | 실습 04: SQL CRUD·RETURNING | PPT 29~34 | 35분
-- SQL 편집: VS Code / 실행: pgAdmin Query Tool (주 경로), psql (선택 경로)
-- @step은 실행 단위를 표시하는 주석입니다. SQL 명령이 아닙니다.
-- 한 @step 구간씩 선택 실행합니다. 오류 뒤 ROLLBACK은 반드시 별도 실행합니다.

-- @step E4_GUARD expect=00000 capture=- reconnect=false
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

-- @step E4_BEFORE expect=00000 capture=- reconnect=false
-- [작업 전 상태 확인] 초기 데이터(S0) 3건의 ID와 내용을 먼저 확인
SELECT id, title, content, category_id FROM public.knowledge ORDER BY id;

-- @step E4_INSERT_BEGIN expect=00000 capture=- reconnect=false
BEGIN;

-- @step E4_INSERT expect=00000 capture=new_ reconnect=false
-- BEGIN TASK B04_01
-- TODO B04_01
-- 지식 한 건을 INSERT하고 생성 결과를 RETURNING으로 받으세요. id는 입력하지 않습니다.
-- 응용·심화는 실제 id를 __NEW_ID__에 넣고 다음 변경을 같은 트랜잭션에서 진행합니다.
-- [핵심 구현 1: INSERT INTO로 새 지식을 추가하고 RETURNING으로 자동 발급된 id와 행 데이터를 즉시 확인]
INSERT INTO public.knowledge (title, content, category_id)
VALUES ('임시 안내', '취소할 연습 데이터입니다.', 1)
RETURNING id, title, content, category_id;
-- END TASK B04_01

-- @step E4_INSERT_CANCEL expect=00000 capture=- reconnect=false
-- [생성 취소] 방금 추가한 임시 안내 행을 취소하여 남기지 않음
ROLLBACK;

-- @step E4_UPDATE_BEFORE expect=00000 capture=- reconnect=false
-- [수정 전 대상 확인] 수정할 대상(id=2, '서버 실행')의 원래 본문 확인
SELECT id,title,content FROM public.knowledge WHERE id=2;

-- @step E4_UPDATE_BEGIN expect=00000 capture=- reconnect=false
BEGIN;

-- @step E4_UPDATE expect=00000 capture=- reconnect=false
-- BEGIN TASK B04_02
-- TODO B04_02
-- 지정한 지식 한 건의 content만 수정하세요. 먼저 같은 ID의 현재 행을 SELECT합니다.
-- ID와 전체 행 수는 바뀌지 않아야 하며 제목·분류를 바꾸지 않습니다.
-- [핵심 구현 2: SET으로 변경할 열(content)을 지정하고 WHERE로 id=2인 행만 정밀 타격하여 수정]
UPDATE public.knowledge
SET content = '수정 연습 안내입니다.'
WHERE id = 2
RETURNING id, title, content;
-- END TASK B04_02

-- @step E4_UPDATE_CANCEL expect=00000 capture=- reconnect=false
-- [수정 취소] 변경했던 id=2의 본문을 원래대로 복원
ROLLBACK;

-- @step E4_DELETE_BEFORE expect=00000 capture=- reconnect=false
-- [삭제 전 대상 확인] 삭제할 대상(id=3, '질문 작성')의 현재 상태 확인
SELECT id,title,content FROM public.knowledge WHERE id=3;

-- @step E4_DELETE_BEGIN expect=00000 capture=- reconnect=false
BEGIN;

-- @step E4_DELETE expect=00000 capture=- reconnect=false
-- BEGIN TASK B04_03
-- TODO B04_03
-- 지정된 ID의 지식만 삭제하고 삭제된 id·title을 반환하세요. 표나 분류를 삭제하지 않습니다.
-- [핵심 구현 3: DELETE FROM과 WHERE를 결합해 id=3인 지식 한 행만 제거하고 삭제된 정보를 반환]
DELETE FROM public.knowledge
WHERE id = 3
RETURNING id, title;
-- END TASK B04_03

-- @step E4_DELETE_CANCEL expect=00000 capture=- reconnect=false
-- [삭제 취소] 삭제했던 id=3 행을 취소하여 다시 복원
ROLLBACK;

-- @step E4_AFTER expect=00000 capture=- reconnect=false
-- [최종 보존 검증] 모든 변경이 ROLLBACK되어 시작 상태(1, 2, 3번 3건)와 동일한지 확인
SELECT id, title, content, category_id FROM public.knowledge ORDER BY id;