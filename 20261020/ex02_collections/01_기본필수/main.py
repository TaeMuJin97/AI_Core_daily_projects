# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 02 | 기본필수
# 점수 List 통계 | PPT 30쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

scores = [82, 95, 76, 88]
# TODO 01: len·sum·max·min을 사용하여 통계를 계산하세요.
count = len(scores)
total = sum(scores)
average_score = total / count
highest = max(scores)
lowest = min(scores)
print(f"점수: {scores}")
print(f"개수: {count}")
print(f"합계: {total}")
print(f"평균: {average_score:.1f}")
print(f"최댓값: {highest}")
print(f"최솟값: {lowest}")
