# 실습 03 · 입력 오류와 텍스트 파일 다루기 · 응용

**PPT 실습 31쪽 · 설명 24~32쪽 · 전체 단계 선택 실습 20분**

## 목표
잘못된 입력에서 다시 입력할 수 있는 반복을 완성하고, 파일 없음과 정상 파일을 구분합니다. 정상·문자·0 입력을 기록합니다.

## 진행 순서
먼저 동작을 예측하고, 아래 TODO를 구현합니다. 직접 실행 → 공개 검사 → 페어 설명/기록 순서로 마칩니다.
TODO가 아닌 입출력 틀·검사 도구·이전 단계 구현은 제공 코드입니다. 파일 간 책임을 바꾸지 않고 핵심 처리부터 완성합니다.

| 수정할 파일 | TODO/해설 번호 | 구현할 내용 |
|---|---|---|
| `main.py` | `RETRY` | q/EOF이면 None, 올바른 수이면 정수를 반환하고 ValueError이면 안내 후 반복하세요. |
| `main.py` | `SAFE-READ` | 읽기에 성공하면 ('ok', text), 파일 없음은 ('missing', 안내), 권한 오류는 ('permission', 안내)를 반환하세요. |

## 실행
가상환경의 Python으로 실행합니다. 현재 난이도 폴더에서:

```text
python main.py
```

역할 폴더(강사용 또는 수강생용)에서 제공 런처를 사용할 때:

```text
python tools/run.py --exercise 03 --level applied
python tools/check.py --exercise 03 --level applied
```

`checks.py`는 기능 확인용 제공 테스트입니다. 검사 도구는 임시 복사본에서 실행하여 원본 소스와 결과물을 변경하지 않습니다.
출력 기대값은 `expected_output.txt`, 생성 파일 예시는 `expected_outputs/`를 확인합니다. 구현을 하드코딩해 예시 한 건만 맞추지 마세요.

## 생성할 결과
- `data/note.txt`

### 함수 계약
parse_count(raw): 문자열을 1 이상의 int로 바꾸거나 ValueError를 전달합니다.
save_note(path,text): UTF-8 w 모드로 저장합니다. 이 실습 전용 note.txt는 재실행하면 교체됩니다.
read_note(path): 줄바꿈까지 포함한 문자열을 반환합니다.
request_count: 잘못된 입력은 재시도, q 또는 EOF는 None 반환입니다.
safe_read_note: (상태, 내용/안내) 튜플을 반환합니다. 상태는 ok/missing/permission이며 예상 밖 장치 오류를 숨기지 않습니다.

### 추가 실행
`python main.py --interactive`에서 abc → 0 → 3을 입력하고 안내 두 번 후 3이 반환되는지 확인합니다. q로 종료할 수 있습니다.
권한 오류는 mock으로 재현합니다. 실제 폴더 권한을 바꾸거나 관리자 권한으로 실행하지 않습니다.


## 완료 확인
구현한 범위의 자동 테스트가 통과하고, 테스트_기록.md에 실제 명령/결과를 기록했는지 확인합니다.
코드를 설명하지 못한 채 출력만 맞춘 경우에는 페어에게 입력 → 처리 → 반환/저장의 순서를 설명해 봅니다.

수강생용: TODO의 NotImplementedError는 미완성 표시입니다. 구현이 끝나면 해당 raise를 제거하세요. 테스트 파일의 기대값을 수정해 통과시키지 않습니다.
