# Day30 · 2026-11-27 개인 일일 프로젝트 실습자료

- `common/README_START.md`: 모든 난이도 공통 시작 안내.
- `common/docs/Day30_SRS_v1.0.html`: 제공된 요구사항명세서 원본.
- `mentee/01_basic`: TODO Skeleton; `02_intermediate`: 폴더만; `03_advanced`: 빈 폴더.
- `mentor/01_basic~03_advanced`: 강사용 독립 참조 구현.
- `common/postman`, `common/data/evaluation`, `common/tests`, `common/docs/acceptance_checklist.csv`: 검증 자료.
- `mentor/INSTRUCTOR_GUIDE.md`: 강사용 운영 및 교실 실환경 검수 안내.

11/20 데이터베이스만 읽기 전용으로 재사용합니다. 신규 DB, 기존 소스 Import, Seed, 재인덱싱은 하지 않습니다. 이 ZIP에는 실제 키, DB 비밀번호, DB dump, 모델 가중치가 포함되어 있지 않습니다.

## 2026-11-26 실환경 오류 반영본
CUDA torch 선행 설치, .env 테스트 ID, RAG 역할별 완료 판단, Agent provider-native Structured Output, pytest 수집 범위 보완을 반영했습니다. 배포 시 정답이 포함된 이 통합 ZIP을 학생에게 그대로 제공하지 마세요. SRS 원본과 난이도별 구현 범위는 유지합니다. 자세한 변경/검수는 `mentor/verification/20261126_PATCH_REPORT.md`를 참조하세요.

## 현업형 단계별 검증 제공
`common/test/`의 000~016번을 프로젝트 루트의 `test/`로 복사해 단계별 실행합니다. `common/prepare_project.py`는 공통 설정과 검증 파일을 복사하며 기존 파일을 덮어쓰지 않습니다. `common/test/README.md` 및 `common/docs/IMPLEMENTATION_ORDER.md` 참고. 기존 pytest, Live, Postman, 업무 코드와 TODO는 유지합니다.
