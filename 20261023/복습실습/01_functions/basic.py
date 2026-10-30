"""01 함수 기본필수: 입력 → 계산 → return → 함수 재사용. 세 TODO만 완성합니다."""

def calculate_amount(price, quantity):
    """입력: 정수 단가·수량. 반환: 정수 금액. 이 단계는 정상 입력만 받습니다."""
    # TODO F_B1: 단가와 수량을 곱한 금액을 반환하세요.
    raise NotImplementedError("F_B1: 단가와 수량을 곱한 금액을 반환하세요.")


def receipt_message(item, amount):
    """예: ("아메리카노", 6000) → "아메리카노: 6000원". 출력하지 말고 반환합니다."""
    # TODO F_B2: 상품명과 금액으로 영수증 문장을 만들어 반환하세요.
    raise NotImplementedError("F_B2: 상품명과 금액으로 영수증 문장을 만들어 반환하세요.")


def describe_order(item, price, quantity):
    """calculate_amount와 receipt_message를 연결합니다."""
    # TODO F_B3: 앞의 두 함수를 호출해 주문 안내 문장을 반환하세요.
    raise NotImplementedError("F_B3: 앞의 두 함수를 호출해 주문 안내 문장을 반환하세요.")


def main():
    # 실행 전 아래 세 줄에 어떤 값이 나올지 적어 봅니다.
    print("금액:", calculate_amount(3000, 2))
    print("문장:", receipt_message("쿠키", 6000))
    print("함수 연결:", describe_order("카페라떼", 4000, 2))

if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as error:
        print("[아직 작성할 곳]", error)
        print("해당 TODO 하나부터 채우고 다시 실행하세요. 힌트는 실습안내.html에 있습니다.")
        raise SystemExit(2)
