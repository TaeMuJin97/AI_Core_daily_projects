# 실습 06 · 아이디어 표 정제와 집계 · 심화

**PPT 실습 60쪽 · 설명 50~61, 89쪽 · 전체 단계 선택 실습 25분**

## 목표
그룹별 total·valid·mean_score를 함께 집계하고 원본/정제·결측·변환 실패를 설명하는 3문장 보고서를 완성합니다.

## 진행 순서
먼저 동작을 예측하고, 아래 TODO를 구현합니다. 직접 실행 → 공개 검사 → 페어 설명/기록 순서로 마칩니다.
TODO가 아닌 입출력 틀·검사 도구·이전 단계 구현은 제공 코드입니다. 파일 간 책임을 바꾸지 않고 핵심 처리부터 완성합니다.

| 수정할 파일 | TODO/해설 번호 | 구현할 내용 |
|---|---|---|
| `main.py` | `AGG` | difficulty별 total(size)·valid(count)·mean_score(mean)을 한 표로 만들고 인덱스를 열로 바꾸세요. |
| `main.py` | `AUDIT` | 원본/정제 행 수, 제거 중복, 원래 점수 결측, 숫자 변환 실패, 정제 점수 결측, 채운 난이도 수를 기록하세요. |

## 실행
가상환경의 Python으로 실행합니다. 현재 난이도 폴더에서:

```text
python main.py
```

역할 폴더(강사용 또는 수강생용)에서 제공 런처를 사용할 때:

```text
python tools/run.py --exercise 06 --level advanced
python tools/check.py --exercise 06 --level advanced
```

`checks.py`는 기능 확인용 제공 테스트입니다. 검사 도구는 임시 복사본에서 실행하여 원본 소스와 결과물을 변경하지 않습니다.
출력 기대값은 `expected_output.txt`, 생성 파일 예시는 `expected_outputs/`를 확인합니다. 구현을 하드코딩해 예시 한 건만 맞추지 마세요.

## 생성할 결과
- `outputs/cleaned_records.json`
- `outputs/group_summary.json`
- `outputs/cleaning_audit.json`
- `outputs/cleaning_report.txt`

### 입력과 출력 계약
sample_data.py와 fixtures/raw_records.json은 PPT 51쪽의 동일한 6행 합성 데이터입니다.
기본필수에서 응용 name은 ['B','B','C']입니다. 아직 중복 제거를 하지 않았습니다.
정제 단계에서는 완전 중복 1행만 제거합니다. 이름이 같아도 점수가 다른 행은 삭제하지 않습니다.
clean_data는 새 DataFrame, group_means는 Series, group_summary는 difficulty/total/valid/mean_score 열의 DataFrame입니다.
정제 후 5행, 점수 결측 2개, 난이도 미정 1개, 응용 평균 75.0을 확인합니다.
그룹 순서는 처음 나타난 기본필수/응용/심화/미정입니다. 심화·미정의 평균은 NaN이며 0점이 아닙니다.
AUDIT의 숫자 변환 실패는 중복 제거 후 원래 결측이 아니었으나 숫자가 되지 못한 항목 수(1개)입니다.

### 산출물 표현
JSON 파일에서는 표준 null로 결측을 표시합니다. 분석 DataFrame 내부의 NaN을 0으로 채우지 않습니다.
출력 도우미와 JSON 파일 쓰기는 제공 코드이며 오늘 pandas read_csv/to_csv의 구현을 요구하지 않습니다.
Pandas 문자열 dtype 표시는 버전에 따라 다를 수 있으므로 문자열 열의 dtype 글자만 맞추는 테스트는 하지 않습니다.


## 완료 확인
구현한 범위의 자동 테스트가 통과하고, 테스트_기록.md에 실제 명령/결과를 기록했는지 확인합니다.
코드를 설명하지 못한 채 출력만 맞춘 경우에는 페어에게 입력 → 처리 → 반환/저장의 순서를 설명해 봅니다.

수강생용: TODO의 NotImplementedError는 미완성 표시입니다. 구현이 끝나면 해당 raise를 제거하세요. 테스트 파일의 기대값을 수정해 통과시키지 않습니다.
