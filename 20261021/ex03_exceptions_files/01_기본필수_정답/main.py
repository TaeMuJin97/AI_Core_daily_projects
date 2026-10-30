"""한글 파일 왕복과 입력 오류 처리. data/note.txt는 이 실습 전용 출력입니다."""
from pathlib import Path
import argparse
BASE = Path(__file__).resolve().parent
NOTE_TEXT = "오늘은 클래스와 파일을 배웁니다.\n"

def note_path():
    # 해설 PATH: 현재 코드 파일을 기준으로 data/note.txt의 절대경로를 반환하세요. cwd에 의존하지 않습니다.
    return Path(__file__).resolve().parent / "data" / "note.txt"

def parse_count(raw):
    """문자열 -> 1 이상의 정수. 변환 성공과 업무 규칙 충족은 별개입니다."""
    # 해설 COUNT: int로 변환한 뒤 1 미만이면 ValueError를 발생시키고 올바른 수를 반환하세요.
    count = int(raw)
    if count < 1:
        raise ValueError("역할 수는 1 이상이어야 합니다")
    return count

def save_note(path, text):
    # 해설 NOTE-SAVE: 부모 폴더를 만들고 with·w·UTF-8을 사용해 text를 저장하세요.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)

def read_note(path):
    # 해설 NOTE-READ: with·r·UTF-8로 읽은 문자열을 그대로 반환하세요.
    with Path(path).open("r", encoding="utf-8") as f:
        return f.read()

def request_count(input_fn=input, output_fn=print):
    """제공된 입출력 함수는 테스트 시 안전한 가짜 입력으로 바꿀 수 있습니다."""
    # 해설 RETRY: q/EOF이면 None, 올바른 수이면 정수를 반환하고 ValueError이면 안내 후 반복하세요.
    while True:
        try:
            raw = input_fn("역할 수(종료 q)> ")
        except EOFError:
            return None
        if raw.strip().casefold() == "q":
            return None
        try:
            return parse_count(raw)
        except ValueError:
            output_fn("1 이상의 정수를 입력하세요")

def safe_read_note(path):
    # 해설 SAFE-READ: 읽기에 성공하면 ('ok', text), 파일 없음은 ('missing', 안내), 권한 오류는 ('permission', 안내)를 반환하세요.
    try:
        return "ok", read_note(path)
    except FileNotFoundError:
        return "missing", "파일이 없습니다. 경로를 확인하세요."
    except PermissionError:
        return "permission", "접근 권한이 없습니다. 저장 위치를 확인하세요."
    # UnicodeDecodeError와 다른 OSError를 이곳에서 빈 문자열로 숨기지 않습니다.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    if args.interactive:
        result = request_count()
        print("종료" if result is None else f"역할 {result}개")
        return
    for raw in ["2", "abc", "0"]:
        try:
            print(f"입력 {raw}: {parse_count(raw)}")
        except ValueError:
            print(f"입력 {raw}: 1 이상의 정수를 입력하세요")
    path = note_path()
    save_note(path, NOTE_TEXT)
    loaded = read_note(path)
    print(path.name)
    print(loaded.strip())
    print("왕복 일치:", loaded == NOTE_TEXT)

if __name__ == "__main__":
    main()
