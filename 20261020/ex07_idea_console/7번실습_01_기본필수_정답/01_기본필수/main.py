# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 07 | 기본필수
# 아이디어 이름 등록·조회 콘솔 | PPT 63쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 강사용: 완성된 정답과 설명 주석. 수강생에게 배포하지 않는다.

def add_idea(ideas, name):
    """이름을 List에 저장한다. 빈 이름은 False를 반환한다."""
    # 해설 01: 공백 정리 후 빈 이름을 거부하고 아이디어 이름을 List에 저장한다.
    cleaned = name.strip()
    if not cleaned:
        return False
    ideas.append(cleaned)
    return True


def format_ideas(ideas):
    """전체 목록을 문자열로 반환한다."""
    # 해설 02: 빈 목록과 번호가 붙은 전체 목록을 문자열로 반환한다.
    if not ideas:
        return "등록된 아이디어가 없습니다."
    lines = []
    for number, name in enumerate(ideas, start=1):
        lines.append(f"{number}. {name}")
    return "\n".join(lines)


def main():
    # 오늘은 메모리의 List만 사용한다. 종료하면 등록 데이터가 사라지는 것이 정상이다.
    ideas = []
    while True:
        print("\n1=등록 | 2=전체 목록 | 0=종료")
        command = input("선택: ").strip()
        if command == "0":
            print("종료합니다.")
            break
        elif command == "1":
            name = input("프로젝트명: ")
            # 해설 03: add_idea를 호출하고 반환값에 따라 안내한다.
            if add_idea(ideas, name):
                print("아이디어 등록 완료.")
            else:
                print("프로젝트명을 입력하세요.")
        elif command == "2":
            # 해설 04: format_ideas의 결과를 화면에 출력한다.
            print(format_ideas(ideas))
        else:
            print("잘못된 명령입니다.")


if __name__ == "__main__":
    main()
