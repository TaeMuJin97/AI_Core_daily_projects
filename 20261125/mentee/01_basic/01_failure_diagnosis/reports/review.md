# 수행 기록 · Day28 실습 01

**실행한 모드:** `offline_fixture` (실습 01은 외부 모델·DB를 호출하지 않는 고정 진단 사례 전용)

**작성 TODO:** `classify_case`, `describe_evidence`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `failure_cases.json`(`dataset_version: "d28-eval-v1"`)의 고정 진단 사례 5건(`F01`, `F02`, `F03`, `F04`, `F05`)을 입력으로 사용함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. Gold 포함 여부(`candidate_has_gold`, `context_has_gold`)는 실행 이후의 사후 실패 위치 진단에만 사용되며 검색·생성 Target 입력에는 전달하지 않음

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 1`, `level: "01_basic"`, `mode: "offline_fixture"`, `dataset_version: "d28-eval-v1"`)에서 5건 모두 `stage`와 1줄 `evidence`가 정상 분류됨
    - `F01` → `retrieval`: 1차 검색 후보에 정답 문서 미포함(`candidate_has_gold=False`)
    - `F02` → `rerank_or_context`: 후보에는 있었으나 최종 Context에서 탈락(`candidate_has_gold=True`, `context_has_gold=False`)
    - `F03` → `generation`: Context에 근거가 있으나 생성 답변이 근거와 불일치(`context_has_gold=True`, `answer_grounded=False`)
    - `F04` → `system_error`: 시스템 장애 발생(`system_error=True`)
    - `F05` → `ok`: 장애 없이 후보·Context·근거 일치 조건 모두 충족
- No-answer / 실패 / 정상의 차이:
  - `F04`(`system_error`) 같은 인프라·API 장애를 검색/생성 품질 실패나 정보 부족으로 위장하지 않고 별도 단계로 분리함
  - 검색 후보 누락(`F01`)과 Context 탈락(`F02`), 생성 환각(`F03`), 정상 통과(`F05`)가 서로 다른 원인과 조치 대상으로 구분됨

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - RAG 파이프라인은 **System → Candidate(Retrieval) → Context(Rerank/Builder) → Generation** 순으로 앞 단계 출력이 다음 단계 입력이 되므로, 앞단 실패를 먼저 판별해야 원인을 오진하지 않음 (후보에 정답이 없는 `F01`을 Reranker나 Prompt 수정으로 해결하려 하면 실패함)
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `system_error`(`F04`) → DB · GPU · API 인증 · 예외 처리
  - `retrieval`(`F01`) → Query Rewrite · 필터 · 임베딩 · 인덱스(Retriever)
  - `rerank_or_context`(`F02`) → Cross-Encoder Reranker · `candidate_k` · Context 길이 예산
  - `generation`(`F03`) → Prompt 지침 · 근거 활용 · 출력 검증

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - 실패 단계별 분류 로그가 남는지뿐 아니라, 허용되지 않은 문서를 차단하는 권한 필터, 실제 `included_ids` 기반 Citation 검증, 시스템 오류 시 `insufficient_context`로 위장하지 않는 오류 계약, 응답 지연(Latency) 기준을 함께 검증해야 함