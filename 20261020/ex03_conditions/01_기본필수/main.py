# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 03 | 기본필수
# 점수에 따른 PASS·REVIEW | PPT 37쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

score = float(input("점수(0~100): "))
# TODO 01: 범위를 벗어난 값은 안내하고, 60 이상은 PASS·미만은 REVIEW를 출력하세요.
print("TODO: 점수를 판정하세요.")
if score < 0 or score > 100:
    print("점수는 0~100 사이여야 합니다.")
elif score >= 60:
    print("PASS")
else:
    print("REVIEW")