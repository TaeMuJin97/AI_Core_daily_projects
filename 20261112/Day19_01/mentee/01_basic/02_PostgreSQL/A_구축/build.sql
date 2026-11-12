/*
==============================================================================
[실습 보고서: Day 19 오전 자율 실습 2A - A_구축/build.sql RDB 스키마 직접 구축]
1. 실험 목적: ERD(ERD.dbml)와 스키마 명세서를 바탕으로 구축 전용 DB(day19_build_b)에
              부모 테이블(categories)과 자식 테이블(knowledge) 및 제약조건을 직접 구현함.
2. 핵심 포인트:
   - 식별자 자동 발급 (B-DDL-01): GENERATED ALWAYS AS IDENTITY PRIMARY KEY로 수동 ID 주입을 막고 PK를 선언함.
   - 빈 문자열 방어 (B-DDL-02, 03): VARCHAR/TEXT의 NOT NULL만으로는 빈 문자열('')을 막지 못하므로
     char_length(...) BETWEEN 최소 AND 최대 CHECK 제약으로 글자 수 범위를 강제함.
   - 참조 무결성 및 삭제 보호 (B-DDL-04): REFERENCES public.categories(id) ON DELETE RESTRICT를 통해
     자식 지식이 연결된 부모 분류가 임의로 삭제되지 않도록 DB 차원에서 보호함.
==============================================================================
*/
BEGIN;
-- 제공 안전장치: 아래 DO 구문은 수정 과제가 아닙니다.
DO $guard$
BEGIN
    IF current_database() <> 'day19_build_b' THEN
        RAISE EXCEPTION 'Wrong database: expected day19_build_b, got %', current_database();
    END IF;
END;
$guard$;

CREATE TABLE public.categories (
    -- BEGIN B-DDL-01
    -- TODO B-DDL-01: categories의 id를 BIGINT 자동 생성 IDENTITY와 PRIMARY KEY로 선언하세요.
    -- 쉼표까지 포함합니다.
    -- [핵심 구현 1: 자동 증가 식별자(IDENTITY) 및 기본키(PRIMARY KEY) 선언]
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- END B-DDL-01
    name VARCHAR(30) NOT NULL UNIQUE,
    -- BEGIN B-DDL-02
    -- TODO B-DDL-02: categories.name의 1~30자 길이 CHECK를 categories_name_length라는
    -- 이름으로 완성하세요.
    -- [핵심 구현 2: 분류명 글자 수 1~30자 제한 CHECK 제약조건]
    CONSTRAINT categories_name_length CHECK (char_length(name) BETWEEN 1 AND 30)
    -- END B-DDL-02
);

CREATE TABLE public.knowledge (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(80) NOT NULL,
    content TEXT NOT NULL,
    category_id BIGINT NOT NULL,
    -- BEGIN B-DDL-03
    -- TODO B-DDL-03: title은 1~80자, content는 1~2000자인 두 CHECK를 명세의 이름으로 완성하세요. 각 줄
    -- 끝 쉼표가 필요합니다.
    -- [핵심 구현 3: 제목(1~80자) 및 본문(1~2000자) 길이 제한 CHECK 제약조건]
    CONSTRAINT knowledge_title_length CHECK (char_length(title) BETWEEN 1 AND 80),
    CONSTRAINT knowledge_content_length CHECK (char_length(content) BETWEEN 1 AND 2000),
    -- END B-DDL-03
    CONSTRAINT knowledge_category_fk FOREIGN KEY (category_id)
        -- BEGIN B-DDL-04
        -- TODO B-DDL-04: category_id가 public.categories(id)를 참조하도록 REFERENCES와 부모 삭제
        -- RESTRICT를 완성하세요.
        -- [핵심 구현 4: 부모 categories(id) 외래키 연결 및 자식 존재 시 부모 삭제 금지(ON DELETE RESTRICT)]
        REFERENCES public.categories(id) ON DELETE RESTRICT
        -- END B-DDL-04
);
COMMIT;