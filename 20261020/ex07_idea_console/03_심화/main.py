# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 07 | 심화
# Agent 역할 List와 테스트 가능한 설계 | PPT 63쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

def normalize_roles(raw_roles):
    """쉼표 구분 문자열을 역할 List로 변환한다. 빈 값과 대소문자 기준 중복을 제거한다."""
    # TODO 01: 쉼표로 나누고 공백·빈 값·대소문자 기준 중복을 제거하세요. 처음 입력한 표기와 순서는 유지하세요.
    raise NotImplementedError("TODO: normalize_roles")


def add_idea(ideas, name, problem, raw_roles, difficulty):
    """검사에 성공한 경우에만 List에 추가한다. 반환값은 (bool, 안내 문자열)이다."""
    name = name.strip()
    problem = problem.strip()
    difficulty = difficulty.strip()
    roles = normalize_roles(raw_roles)
    # TODO 02: 필수값·허용 난이도·프로젝트명 중복을 검사한 뒤 Dict를 추가하고 (성공 여부, 안내)를 반환하세요.
    raise NotImplementedError("TODO: add_idea")


def search_ideas(ideas, keyword):
    """프로젝트명·문제·역할을 부분 검색한다. 빈 검색어는 빈 List를 반환한다."""
    # TODO 03: 프로젝트명·문제·역할을 대소문자 구분 없이 부분 검색하세요.
    raise NotImplementedError("TODO: search_ideas")


def filter_by_difficulty(ideas, difficulty):
    """정확히 일치하는 난이도의 아이디어를 선택한다. 원본을 변경하지 않는다."""
    # TODO 04: 난이도가 정확히 일치하는 아이디어만 반환하세요.
    raise NotImplementedError("TODO: filter_by_difficulty")


def count_by_difficulty(ideas):
    """모든 난이도를 0부터 집계하여 고정된 세 키를 가진 Dict로 반환한다."""
    # TODO 05: 기본필수·응용·심화의 개수를 0부터 집계하세요.
    raise NotImplementedError("TODO: count_by_difficulty")


def format_ideas(ideas):
    """한 아이디어를 세 줄로 표현한 뒤 전체를 연결한다."""
    # TODO 06: 원본 정보를 유지하면서 예상 출력 형식의 목록 문자열을 만드세요.
    raise NotImplementedError("TODO: format_ideas")


def print_menu():
    print("\n1=등록 | 2=전체 목록 | 3=검색 | 4=난이도 필터 | 5=난이도 통계 | 0=종료")


def main():
    ideas = []
    while True:
        print_menu()
        command = input("선택: ").strip()
        if command == "0":
            print("종료합니다.")
            break
        elif command == "1":
            name = input("프로젝트명: ")
            problem = input("해결할 문제: ")
            roles = input("Agent 역할: ")
            difficulty = input("난이도(기본필수/응용/심화): ")
            # TODO 07: 등록 함수를 호출하고 반환된 안내 문장을 출력하세요.
            print("TODO: 등록 함수를 연결하세요.")
        elif command == "2":
            print(format_ideas(ideas))
        elif command == "3":
            keyword = input("검색어: ")
            if not keyword.strip():
                print("검색어를 입력하세요.")
                continue
            matches = search_ideas(ideas, keyword)
            if matches:
                print(format_ideas(matches))
            else:
                print("검색 결과가 없습니다.")
        elif command == "4":
            difficulty = input("필터 난이도: ").strip()
            if difficulty not in ("기본필수", "응용", "심화"):
                print("난이도는 기본필수·응용·심화 중 하나여야 합니다.")
                continue
            matches = filter_by_difficulty(ideas, difficulty)
            if matches:
                print(format_ideas(matches))
            else:
                print("해당 난이도의 아이디어가 없습니다.")
        elif command == "5":
            # TODO 08: 집계 함수를 호출하여 난이도별 개수를 출력하세요.
            print("TODO: 통계 함수를 연결하세요.")
        else:
            print("잘못된 명령입니다.")


if __name__ == "__main__":
    main()
