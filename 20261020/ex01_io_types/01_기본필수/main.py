# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 01 | 기본필수
# 내년 나이와 학습시간 출력 | PPT 21쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

# input()으로 받은 값은 모두 문자열이다.
name = input("이름: ")
age_text = input("현재 나이: ")
hours_text = input("하루 학습시간: ")
# TODO 01: 나이를 int, 학습시간을 float로 변환하세요.
age = int(age_text)
hours = float(hours_text)
# TODO 02: 현재 나이에 1을 더해 next_age에 저장하세요.
next_age = age + 1
# TODO 03: 이름·내년 나이·학습시간을 예상 형식으로 출력하세요.
# print("TODO: 내년 나이와 학습시간을 출력하세요.")
print(f"이름: {name}")
print(f"내년 나이: {next_age}")
print(f"하루 학습시간: {hours}")