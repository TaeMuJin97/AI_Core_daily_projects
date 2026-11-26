# Intermediate · 기능별 분리

- `main.py`: 실습 실행 진입점
- `tasks.py`: 주요 2개 TODO 구현(입력·처리 중심)
- `validation_XX.py`: 검증·출력 확장 TODO 1개
- `coursekit/`(루트): DB·GPU·Tool Agent의 실제 접속/호출 기능

중복 구현 없이 각 함수의 책임을 나누고 실제 DB 값을 관찰합니다.
