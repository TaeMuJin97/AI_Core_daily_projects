# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 07 | 기본필수
# 아이디어 이름 등록·조회 콘솔 | PPT 63쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

def add_idea(ideas, name):
    """이름을 List에 저장한다. 빈 이름은 False를 반환한다."""
    # TODO 01: 공백 정리 후 빈 이름을 거부하고 아이디어 이름을 List에 저장하세요.
    # raise NotImplementedError("TODO 1: add_idea")
    name = name.strip()
    if not name:
        return False
    ideas.append(name)
    return True

def format_ideas(ideas):
    """전체 목록을 문자열로 반환한다."""
    # TODO 02: 빈 목록과 번호가 붙은 전체 목록을 문자열로 반환하세요.
    # raise NotImplementedError("TODO 2: format_ideas")
    if not ideas:
        return "등록된 아이디가 없습니다."
    
    result = []
    for i, idea in enumerate(ideas, start=1):
        result.append(f"{i}. {idea}")
    return "\n".join(result)

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
            if add_idea(ideas,name):
                print("아이디어를 등록했습니다.")
            # TODO 03: add_idea를 호출하고 반환값에 따라 안내하세요.
            else:
                print("공백은 등록할 수 없습니다.")

        elif command == "2":
            print(format_ideas(ideas))
            # TODO 04: format_ideas의 결과를 화면에 출력하세요.
            
        else:
            print("잘못된 명령입니다.")


if __name__ == "__main__":
    main()
