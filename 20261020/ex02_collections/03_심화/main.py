# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 02 | 심화
# 두 팀의 기술 비교와 Tuple 언패킹 | PPT 30쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

team_a = {"Python", "Git", "SQL"}
team_b = {"Python", "Docker", "Git"}
# TODO 01: &·|·-로 공통·전체·A만·B만의 기술을 계산하세요.
common = set()
all_skills = set()
only_a = set()
only_b = set()
# TODO 02: 네 결과를 Tuple로 묶고 다른 네 변수로 언패킹하세요.
result = ()
common_result = set()
all_result = set()
a_result = set()
b_result = set()
# [제공 코드] sorted()는 출력 순서를 고정한 새 List를 만든다. Set 자체의 순서는 보장되지 않는다.
print("공통 기술:", sorted(common_result))
print("전체 기술:", sorted(all_result))
print("A팀만:", sorted(a_result))
print("B팀만:", sorted(b_result))
