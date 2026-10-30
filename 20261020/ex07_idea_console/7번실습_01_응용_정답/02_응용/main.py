# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 07 | 응용
# Dict 기반 검색·필터·중복·통계 | PPT 63쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 강사용: 완성된 정답과 설명 주석. 수강생에게 배포하지 않는다.

def add_idea(ideas, name, problem, raw_roles, difficulty):
    """검사에 성공한 경우에만 List에 추가한다. 반환값은 (bool, 안내 문자열)이다."""
    name = name.strip()
    problem = problem.strip()
    difficulty = difficulty.strip()
    roles = raw_roles.strip()
    # 해설 01: 필수값·허용 난이도·프로젝트명 중복을 검사한 뒤 Dict를 추가하고 (성공 여부, 안내)를 반환한다.
    # 모든 검사를 통과한 뒤에만 append한다. 실패 시 입력 List를 바꾸지 않는다.
    if not name or not problem or not roles:
        return False, "프로젝트명·문제·역할을 모두 입력하세요."
    if difficulty not in ("기본필수", "응용", "심화"):
        return False, "난이도는 기본필수·응용·심화 중 하나여야 합니다."
    for idea in ideas:
        if idea["name"].strip().lower() == name.lower():
            return False, "이미 등록된 프로젝트명입니다."
    ideas.append({"name": name, "problem": problem, "roles": roles, "difficulty": difficulty})
    return True, "아이디어 등록 완료."


def search_ideas(ideas, keyword):
    """프로젝트명·문제·역할을 부분 검색한다. 빈 검색어는 빈 List를 반환한다."""
    # 해설 02: 프로젝트명·문제·역할을 대소문자 구분 없이 부분 검색한다.
    keyword = keyword.strip().lower()
    if not keyword:
        return []
    result = []
    for idea in ideas:
        role_text = idea["roles"]
        text = f"{idea['name']} {idea['problem']} {role_text}".lower()
        if keyword in text:
            result.append(idea)
    return result


def filter_by_difficulty(ideas, difficulty):
    """정확히 일치하는 난이도의 아이디어를 선택한다. 원본을 변경하지 않는다."""
    # 해설 03: 난이도가 정확히 일치하는 아이디어만 반환한다.
    difficulty = difficulty.strip()
    result = []
    for idea in ideas:
        if idea["difficulty"] == difficulty:
            result.append(idea)
    return result


def count_by_difficulty(ideas):
    """모든 난이도를 0부터 집계하여 고정된 세 키를 가진 Dict로 반환한다."""
    # 해설 04: 기본필수·응용·심화의 개수를 0부터 집계한다.
    counts = {"기본필수": 0, "응용": 0, "심화": 0}
    for idea in ideas:
        counts[idea["difficulty"]] += 1
    return counts


def format_ideas(ideas):
    """한 아이디어를 세 줄로 표현한 뒤 전체를 연결한다."""
    # 해설 05: 원본 정보를 유지하면서 예상 출력 형식의 목록 문자열을 만드세요.
    if not ideas:
        return "등록된 아이디어가 없습니다."
    lines = []
    for number, idea in enumerate(ideas, start=1):
        role_text = idea["roles"]
        lines.append(f"{number}. {idea['name']} | 난이도: {idea['difficulty']}")
        lines.append(f"   문제: {idea['problem']}")
        lines.append(f"   역할: {role_text}")
    return "\n".join(lines)


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
            # 해설 06: 등록 함수를 호출하고 반환된 안내 문장을 출력한다.
            success, message = add_idea(ideas, name, problem, roles, difficulty)
            print(message)
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
            # 해설 07: 집계 함수를 호출하여 난이도별 개수를 출력한다.
            counts = count_by_difficulty(ideas)
            for difficulty, count in counts.items():
                print(f"{difficulty}: {count}개")
        else:
            print("잘못된 명령입니다.")


if __name__ == "__main__":
    main()
