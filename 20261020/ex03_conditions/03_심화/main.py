# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 03 | 심화
# 연령·회원 요금의 경계값 검증 | PPT 37쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

age = int(input("나이: "))
member = input("회원(y/n): ")
if age < 0 or member not in ("y", "n"):
    print("나이는 0 이상, 회원 여부는 y 또는 n으로 입력하세요.")
else:
    # TODO 01: 19세 미만 8,000원·65세 이상 7,000원·그 외 12,000원으로 분기하세요.
    fee = 0
    # TODO 02: 회원인 경우 선정한 요금을 10% 할인하세요.
    pass
    print(f"최종 요금: {fee:,}원")
