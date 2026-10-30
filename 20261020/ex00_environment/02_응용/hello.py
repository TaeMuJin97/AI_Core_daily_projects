# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 00 | 응용
# 변수와 f-string으로 인사하기 | PPT 13쪽
# 실행: python hello.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

# TODO 01: course="AI 개발", day=2, name="민지"가 되도록 변수를 선언하세요.
course = "AI 개발"
day = 2
name = "민지"
# TODO 02: 세 변수를 f-string으로 연결해 예상 문장을 만드세요.
message = f"안녕하세요, {name}님! 오늘은 {course} Day {day}입니다."
print(message)
