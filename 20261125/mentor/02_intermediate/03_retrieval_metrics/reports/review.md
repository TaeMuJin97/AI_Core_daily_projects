# 수행 기록 · Day28 실습 03

**실행한 모드:** (offline_fixture / live 중 실제 실행을 기록)

**작성 TODO:** calculate_recall, count_gold_hits, precision_and_hit

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
- Gold Label을 Target 입력에 전달하지 않았는가?

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
- No-answer / 실패 / 정상의 차이:

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?

## 강사 해설 포인트
Recall의 분모는 전체 Gold 개수, Precision의 분모는 k입니다.
질문과 Gold는 별도 입력으로 관리합니다. 출력의 지표/오류/출처가 원문과 연결되는지 직접 확인해야 합니다.
