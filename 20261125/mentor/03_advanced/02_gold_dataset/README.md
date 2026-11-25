# Day28 실습 02 · Gold Dataset 설계 · 03_advanced

**강의 연결:** 2026-11-25, Day28 최종 HTML **18페이지** · Gold Label · Dataset

## 무엇을 학습하나요?

질문별 Gold 문서와 무정답 질문을 구분합니다.

Gold는 사람이 정한 관련 문서/청크 ID 집합이고 Target에 넣으면 누출입니다.

## 준비사항

- Python 3.12, Windows 11, VS Code, Git Bash, 프로젝트 역할 루트의 `.venv`
- 강의 HTML 68페이지에서 해당 실습 안내를 먼저 확인
- 공통 데이터는 역할 폴더의 `data/`를 사용. 이전 날짜 과제 완료 여부와 무관하게 시작 가능

## 사용할 파일

- `app/datasets/labels.py`: 기능/검증 단위
- `app/datasets/validation.py`: 기능/검증 단위
- `app/audit/revisions.py`: 기능/검증 단위

## TODO 요구사항 — 수강생 체크리스트

- **D28-02-A01 · `select_gold()`**: gold[question_id]에서 관련 청크 ID 목록을 읽어 중복 없는 list로 반환하세요. 모델 검색 결과를 입력으로 쓰지 마세요.  \n  **힌트:** Gold는 Retriever의 정답이 아니라 평가용 레이블입니다.
- **D28-02-A02 · `validate_gold_ids()`**: ID 중복이 없고 모든 ID가 Corpus에 실제 존재하는지 검사하세요.  \n  **힌트:** set의 길이와 corpus.keys()를 활용하세요.
- **D28-02-A03 · `label_no_answer()`**: Gold가 비어 있는 질문은 No-answer로 분리하는 bool을 반환하세요.  \n  **힌트:** Gold가 없는 질문의 Recall을 0점으로 평균내면 안 됩니다.
- **D28-02-A04 · `audit_gold()`**: question_id·Gold ID·데이터셋 버전·고정 여부를 포함하는 감사 기록을 만드세요. 평가 결과로 Gold를 수정하지 않습니다.  \n  **힌트:** 현재 레이블은 실제 기관 전문가의 판정이 아닌 교육용 예시입니다.

## 실행 명령 (VS Code Git Bash, `mentor/` 기준)

```bash
python 03_advanced/02_gold_dataset/main.py --offline
python -m pytest -q 03_advanced/02_gold_dataset/tests
```

실습 06~08은 **TODO 완성 후**, CUDA·PostgreSQL·LLM API 환경 준비 시 아래 실제 경로도 실행할 수 있습니다.

```bash
python 03_advanced/02_gold_dataset/main.py --live
```

- **`--offline`(기본):** 실제 모델/DB를 호출하지 않는 고정 교육용 사례입니다. 결과가 좋아도 모델 성능이라 주장하지 마세요.
- **`--live`:** 06~08에서만 지원하며 실제 LangChain·E5(CUDA)·pgvector·Cross-Encoder(CUDA)·ChatOpenAI를 사용합니다. 외부 호출 비용 및 사전 DB 준비가 필요합니다.
- 실패 시 어느 TODO인지 확인하고 먼저 작은 입력으로 테스트하세요. 수강생 버전은 미완성 TODO를 실행하면 오류가 나도록 설계되어 있습니다.

## 결과물과 완료기준

- `outputs/result.json` : 수행 결과. `mode`, `question_id`, 평가값과 No-answer 처리 여부 확인
- `expected/EXPECTED.md` : 결과 필드와 해석 방법 확인
- `reports/review.md` : 본인 출력·오류·해석·다음 날 Agent와의 연결 기록
- **완료 기준:** 질문별 Gold 문서와 무정답 질문을 구분합니다. Gold/정답 레이블이 실행 대상 Target으로 누출되지 않고, 평가 결과를 구체적인 질문·문서 ID로 설명할 수 있어야 합니다.

## 현업에서 중요한 점

- `question_id`와 데이터·코드 버전으로 실행을 재현할 수 있도록 합니다.
- Gold 없는 No-answer는 일반 Retrieval 지표 평균과 분리합니다.
- Retrieval 지표와 Generation의 Claim/답변 검토는 서로 다른 판단입니다.
- Day29 Agent Tool로 연결하기 전에는 출처·권한·오류도 검증해야 합니다.
