# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 05 | 심화
# 전역 상태 없는 함수형 메뉴 | PPT 54쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

def print_menu():
    """메뉴 출력만 담당한다. 처리할 데이터는 이 함수에 필요하지 않다."""
    # TODO 01: print_menu는 메뉴만 출력하도록 작성하세요.
    raise NotImplementedError("TODO 1: print_menu")


def add_item(items, item):
    """빈 항목이면 False, 저장하면 True. 전달받은 List를 변경한다는 계약을 명시한다."""
    # TODO 02: 앞뒤 공백을 정리하고 비어 있지 않은 항목만 추가한 뒤 성공 여부를 반환하세요.
    raise NotImplementedError("TODO 2: add_item")


def show_items(items):
    """항목을 읽어서 화면에 표시한다. items 자체는 변경하지 않는다."""
    # TODO 03: 빈 목록 안내 또는 번호가 붙은 목록을 출력하세요.
    raise NotImplementedError("TODO 3: show_items")


def main():
    # 상태를 main의 지역 변수로 두고 필요한 함수에 명시적으로 전달한다.
    items = []
    while True:
        print_menu()
        command = input("선택: ")
        if command == "0":
            print("종료합니다.")
            break
        elif command == "1":
            item = input("추가할 항목: ")
            # TODO 04: add_item의 반환값을 사용해 성공 또는 실패를 안내하세요.
            print("TODO: add_item을 호출하세요.")
        elif command == "2":
            # TODO 05: items를 show_items에 전달하세요.
            print("TODO: show_items를 호출하세요.")
        else:
            print("잘못된 명령입니다. 다시 입력하세요.")


if __name__ == "__main__":
    main()
