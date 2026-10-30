"""수정할 TODO가 없는 첫 성공 경험. 실행 → 값 하나 변경 → 다시 실행."""

def double(number):
    # number는 이 함수가 받은 입력값입니다.
    result = number * 2
    return result


if __name__ == "__main__":
    answer = double(3)
    print("3을 두 배:", answer)
    print("문자열 숫자:", "2" + "3")
    print("정수 덧셈:", int("2") + int("3"))
    print("실행 성공. 이제 double(3)을 double(4)로 바꿔 다시 실행하세요.")
