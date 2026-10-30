"""실행 진입점: 반드시 day3_console에서 python -m idea_app.main으로 실행합니다."""
from idea_app.models import Idea
from idea_app.service import IdeaCatalog

def main():
    # 제공 코드 MAIN: Idea 두 개를 만들고 catalog에 등록한 뒤 names() 결과를 출력하세요.
    catalog = IdeaCatalog()
    catalog.add(Idea("문서", "검색", ["Researcher", "Writer"], "응용"))
    catalog.add(Idea("학습", "복습", ["Tutor"], "기본필수"))
    print(catalog.names())

if __name__ == "__main__":
    main()
