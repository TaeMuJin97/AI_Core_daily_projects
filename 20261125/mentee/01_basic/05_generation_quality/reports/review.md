# 수행 기록 · Day28 실습 05

**실행한 모드:** `offline_fixture` (실습 05는 외부 LLM·DB를 호출하지 않는 사람 판정 기반 `human_fixture` 레이블 계산 전용)

**작성 TODO:** `claim_faithfulness`, `describe_claim_result`

## 1. 질문·입력
- 어떤 `question_id`를 사용했는가?
  - `generation_claims.json`(`dataset_version: "d28-eval-v1"`)의 생성 평가 사례 4건(`G01`, `G02`, `G03`, `G04`)과 각 사례의 Claim 목록(`supported` 사람 판정 레이블, `label_source: "human_fixture"`)을 입력으로 사용함
- Gold Label을 Target 입력에 전달하지 않았는가?
  - 예. `supported` 레이블과 `Reference Answer`는 생성 Target 입력이 아니라 사후 Generation 평가 단계(`claim_faithfulness`, `describe_claim_result`)에서만 사용됨

## 2. 실제 확인한 출력
- 결과 JSON과 핵심 점수·출처 ID:
  - `outputs/result.json` (`exercise: 5`, `level: "01_basic"`, `mode: "offline_fixture"`, `dataset_version: "d28-eval-v1"`)에서 4건 모두 정상 산출됨 (`pytest` 통과)
    - `G01` → `faithfulness: 0.6666666666666666` (`2/3`), `reason`: `"비지원 Claim 1건 발견: 벌금이 5만원 — 제공된 Context에서 지지되지 않습니다."`
    - `G02` → `faithfulness: 0.0` (`0/1`), `reason`: `"비지원 Claim 1건 발견: 내일 오후 6시 마감 — 제공된 Context에서 지지되지 않습니다."`
    - `G03` → `faithfulness: 1.0` (`1/1`), `reason`: `"모든 Claim 지원 (1/1): 모든 주장이 제공된 Context에서 확인되었습니다 (Reference Answer와의 정답성은 별도 평가)."`
    - `G04` → `faithfulness: null` (`None`), `reason`: `"Claim 없음: 평가할 주장이 0개이므로 Faithfulness는 None(N/A)으로 처리합니다."`
- No-answer / 실패 / 정상의 차이:
  - `G01`은 3개 주장 중 2개만 근거가 있고 1개(`벌금이 5만원`)가 근거 밖 주장으로 부분 충실(`0.667`), `G02`는 유일한 주장(`내일 오후 6시 마감`)이 근거에 없어 완전 비충실(`0.0`)로 판정됨
  - `G03`은 모든 주장이 Context에서 지지되어 정상(`1.0`)으로 분류된 반면, `G04`는 평가할 Claim 자체가 0개이므로 `1.0`(모든 Claim 지원)으로 오인하지 않고 `null(None, N/A)`로 명확히 구분함

## 3. 해설
- 왜 이 공식 또는 분기 조건이 필요한가?
  - 하나의 답변 안에 근거가 있는 사실과 근거 없는 환각이 섞여 있을 수 있으므로(`G01` 사례), 답변 전체가 아닌 **Claim 단위로 분해해 `지원 Claim 수 / 전체 Claim 수` 비율**을 계산해야 정확한 비지원 구간을 찾을 수 있음
  - 주장이 0개인 `G04`를 `1.0`으로 처리하면 빈 응답이나 무내용 답변이 100% 충실한 것으로 왜곡되므로 반드시 `None`으로 분리해야 하며, `Faithfulness`는 제공된 Context와의 일치만 보므로 질문 적합성(`Relevance`)·기준 정답과의 일치(`Correctness`)와 별도로 평가해야 함
- 평가 결과가 좋지 않다면 다음에 수정할 모듈은 어디인가?
  - `G01`·`G02`처럼 Context에 없는 숫자·기한을 지어내 `Faithfulness`가 낮다면, Retriever를 고치기 전에 **System Prompt의 근거 외 추론 금지 지침, `insufficient_context` 거절 규칙, Generator 모델 및 출력 검증 단계**를 우선 점검해야 함

## 4. 11월 26일 Agent와 연결
- Agent가 이 RAG 검색 Tool을 사용하기 전에 추가로 확인해야 할 것은 무엇인가?
  - 출처 ID(`source_ids`)가 존재한다고 해서 `Faithfulness`가 자동으로 1.0이 되는 것은 아니므로, 근거 부족 시 `G02`처럼 임의 날짜를 생성하지 않고 안전하게 거절(`insufficient_context`)하는지, `Relevance`·`Correctness` 기준 및 사람 검수(Human Review) 샘플링 체계가 함께 갖춰져 있는지 확인해야 함