"""01 함수 심화(선택): 입력 검증. 오늘은 상속·데코레이터를 배우지 않습니다."""

def parse_quantity(value):
    """int 또는 정수 문자열만 허용합니다. 1 이상 → int, 나머지 → None."""
    # 해설 F_D1: 수량을 양의 정수로 바꾸고 잘못된 값이면 None을 반환하세요.
    # bool도 int의 한 종류로 취급되므로 별도로 제외합니다.
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        quantity = int(value)
    except ValueError:
        # 빈 문자열, "두 개", "2.5"는 정수로 변환할 수 없습니다.
        return None
    if quantity <= 0:
        return None
    return quantity


def summarize_quantities(values):
    """반환: (유효 수량 합계, 제외 건수). 입력 목록은 변경하지 않습니다."""
    # 해설 F_D2: 유효한 수량의 합과 제외한 값의 개수를 함께 반환하세요.
    total = 0
    rejected = 0
    for value in values:
        quantity = parse_quantity(value)
        if quantity is None:
            rejected = rejected + 1
        else:
            total = total + quantity
    # 두 결과를 튜플로 반환하므로 호출부에서 각각 받을 수 있습니다.
    return total, rejected


def main():
    values = ["2", " 3 ", "", "두 개", "-1", 0, None, 1.5, True]
    total, rejected = summarize_quantities(values)
    print("유효 수량 합:", total)
    print("제외 건수:", rejected)
    print("원본 값 수:", len(values))

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
