# 실습 08 · 최종 검증·설명·다음 수업 준비 · 응용

PPT 76~82쪽 · 해당 교시 실습 35분 · 현재 폴더: `ex08_review/02_응용`

**아직 구현하지 않은 학생 코드의 실패는 정상입니다.** TODO 번호를 찾아 완성하세요.

## 목표
별도 프로세스 복원과 동료 재현으로 저장 결과를 대조한다.

## 입력과 사전 준비
같은 난이도 `ex07_project/.../day5_ml/outputs`의 본인 생성 결과

07~08은 같은 프로젝트를 사용합니다. 08부터 실행하면 파일 없음 오류가 나므로 07부터 완성하세요.

## 구현 위치와 함수 계약
**`review.py::fresh_restore` — D5-08-A1**

신뢰 승인이 있어야 restore_check.py를 현재 실행기의 새 프로세스로 실행합니다. 인자 리스트로 subprocess.run(check=True,capture_output=True,text=True,encoding='utf-8'). 반환값은 복원 스크립트의 JSON stdout을 파싱한 dict입니다. shell=True는 사용하지 않습니다.


## 진행 순서
1. `학습기록.md`에 입력과 예상 결과를 먼저 적습니다.
2. 위 함수의 TODO를 구현합니다. 제공된 입출력·재사용 코드는 그대로 둡니다.
3. 실행하고 예상값과 실제값을 대조합니다. `expected_outputs` 파일을 읽어 정답을 복사하지 않습니다.
4. 자동 검사를 실행하고 실패 메시지의 함수/조건을 확인합니다.
5. 코드가 맞아도 판단 이유·시점·정책을 본인의 말로 설명합니다.

## 힌트
07에서 같은 난이도의 프로젝트를 실행한 뒤 진행합니다. 검증기는 학습을 다시 하지 않습니다. joblib 복원은 직접 생성한 모델인 경우에만 신뢰를 승인하세요.

## 실행·검사 (현재 역할 폴더에서)
```text
python tools/run.py --exercise 08 --level applied
python tools/check.py --exercise 08 --level applied
```
응용/심화의 새 프로세스 복원은 직접 생성한 모델인지 확인한 뒤 `python tools/run.py --exercise 08 --level applied -- --trust-local-model`로 실행합니다. 신뢰 승인이 없으면 복원만 SKIPPED로 표시하며 검증 완료로 간주하지 않습니다.
가상환경을 활성화하지 않았다면 python 대신 `.venv`의 실행기 경로를 사용합니다.

## 완료 결과
검증 출력 + 07 프로젝트의 보고서·테스트 기록·README·Git 이력

비교용: `expected_output.txt` (자동 검사 부분; 수동 리뷰/Git 완료와 구분)
실습 07/08의 자동 검사는 통합된 이전 기능에도 의존합니다. 먼저 동일 난이도 07의 TODO를 완료하세요.

