# -*- coding: utf-8 -*-
# 2026-10-20 Day 2 | 실습 04 | 심화
# while 메뉴와 작업 List | PPT 45쪽
# 실행: python main.py (이 파일이 있는 폴더에서)
# 입력·완료 기준·예상 결과: 같은 폴더의 README.md, sample_input.txt, expected_output.txt
# 수강생용: TODO 부분을 완성한다. 제공된 입출력 형식과 함수 이름은 유지한다.
# NotImplementedError는 미완성 위치를 알리는 표식이다. 해당 줄을 실제 구현으로 교체한다.

items = []
while True:
    print("\n1=추가 | 2=목록 | 0=종료")
    command = input("선택: ")
    if command == "0":
        print("종료합니다.")
        break
    elif command == "1":
        # [제공 코드] strip()은 앞뒤 공백을 제거한다. 자세한 문자열 처리는 7교시에서 다룬다.
        item = input("추가할 항목: ").strip()
        # TODO 01: 빈 항목을 거부하고 유효한 항목은 List 끝에 추가하세요.
        print("TODO: 항목 추가를 구현하세요.")
    elif command == "2":
        # TODO 02: 빈 목록을 처리하고 항목이 있으면 번호와 함께 출력하세요.
        print("TODO: 목록 출력을 구현하세요.")
    else:
        # TODO 03: 잘못된 명령을 안내한 뒤 다시 입력받게 하세요.
        print("TODO: 잘못된 명령 안내를 작성하세요.")
