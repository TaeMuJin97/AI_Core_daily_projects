# Advanced · 실무 책임 분리

- `main.py`: 실제 API·DB·CUDA 실행 진입점
- `tasks.py`: 주요 개념·Tool 구현 TODO
- `policy_XX.py`: 계약 검증·오류·정책·감사 TODO
- `coursekit/`(루트): 공통 Repository / GPU Encoder / Agent Harness

**계약:** 기존 report_agent_lab만 SELECT, 실제 모델 Tool Call과 Python Tool 실행 분리, 원문 비저장 감사, 거부 정책 Fail Closed.

모델이 Tool 호출을 생략할 수 있으므로 호출 결과의 개수는 하드코딩한 성공 기준이 아닙니다.
