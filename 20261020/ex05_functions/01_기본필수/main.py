# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 05 | 기본필수
# 세 함수의 입력과 반환값 | PPT 54쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

def add(a, b):
    """두 숫자를 더한 값을 반환한다. 화면 출력은 호출한 곳에서 담당한다."""
    # TODO 01: 두 숫자의 합을 return으로 반환하세요.
    # raise NotImplementedError("TODO 1: add")
    return a+b

def average(values):
    """숫자 List의 평균을 반환한다. 이 실습에서는 빈 List의 반환값을 0.0으로 정한다."""
    # TODO 02: 빈 List는 0.0, 나머지는 평균을 반환하세요.
    # raise NotImplementedError("TODO 2: average")
    if len(values) == 0:
        return 0.0
    else:
        return sum(values) / len(values)

def format_result(name, value):
    """이름과 숫자를 받아 '이름: 소수점 한 자리' 형태의 문자열을 반환한다."""
    # TODO 03: 이름과 값을 소수점 한 자리 문자열로 반환하세요.
    # raise NotImplementedError("TODO 3: format_result")
    return f"{name}: {value:.1f}"

def main():
    # 각 함수를 두 번 호출한다. 인수를 바꾸어 같은 기능을 재사용한다.
    print(f"add 결과 1: {add(3, 5)}")
    print(f"add 결과 2: {add(-2, 7)}")
    print(f"average 결과 1: {average([80, 90, 100]):.1f}")
    print(f"average 결과 2: {average([]):.1f}")
    print(format_result("민지", 85.25))
    print(format_result("준호", 0))


# [제공 코드] 직접 실행할 때만 main()을 호출한다. 모듈 상세는 다음 수업에서 학습한다.
if __name__ == "__main__":
    main()
