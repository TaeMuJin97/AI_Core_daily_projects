# 실습 05 · 역할별 지연시간 배열 분석 · 응용

**PPT 실습 48쪽 · 설명 42~49, 87~88쪽 · 전체 단계 선택 실습 25분**

## 목표
axis=0/1의 의미를 구분해 역할별·요청별 평균을 계산하고 200ms 이상인 값 4개를 선택합니다.

## 진행 순서
먼저 동작을 예측하고, 아래 TODO를 구현합니다. 직접 실행 → 공개 검사 → 페어 설명/기록 순서로 마칩니다.
TODO가 아닌 입출력 틀·검사 도구·이전 단계 구현은 제공 코드입니다. 파일 간 책임을 바꾸지 않고 핵심 처리부터 완성합니다.

| 수정할 파일 | TODO/해설 번호 | 구현할 내용 |
|---|---|---|
| `main.py` | `AXIS` | 역할별/요청별 평균과 200ms 이상인 값·개수를 계산하세요. |

## 실행
가상환경의 Python으로 실행합니다. 현재 난이도 폴더에서:

```text
python main.py
```

역할 폴더(강사용 또는 수강생용)에서 제공 런처를 사용할 때:

```text
python tools/run.py --exercise 05 --level applied
python tools/check.py --exercise 05 --level applied
```

`checks.py`는 기능 확인용 제공 테스트입니다. 검사 도구는 임시 복사본에서 실행하여 원본 소스와 결과물을 변경하지 않습니다.
출력 기대값은 `expected_output.txt`, 생성 파일 예시는 `expected_outputs/`를 확인합니다. 구현을 하드코딩해 예시 한 건만 맞추지 마세요.

## 생성할 결과
- `outputs/latency_summary.json`

### 입력과 출력 계약
입력은 [[100,200],[150,250],[200,300]], 행=요청, 열=Planner/Researcher, 단위=ms입니다.
basic_stats의 키: shape(List), mean_ms(float), max_ms(float), seconds(List[List]).
axis_stats의 키: by_role, by_request, selected_ms, selected_count.
add_offsets는 원본을 변경하지 않고 같은 shape의 새 배열을 반환합니다.
view_copy_demo의 키: after_view, after_copy_original, copy.
기대: 평균 200ms, 최댓값 300ms, 역할별 [150,250], 요청별 [150,200,250], 200ms 이상 4개.
빈 배열 평균은 계산하지 않고 제공된 check_matrix가 먼저 거부합니다. 벡터화가 GPU 실행을 뜻하지는 않습니다.


## 완료 확인
구현한 범위의 자동 테스트가 통과하고, 테스트_기록.md에 실제 명령/결과를 기록했는지 확인합니다.
코드를 설명하지 못한 채 출력만 맞춘 경우에는 페어에게 입력 → 처리 → 반환/저장의 순서를 설명해 봅니다.

수강생용: TODO의 NotImplementedError는 미완성 표시입니다. 구현이 끝나면 해당 raise를 제거하세요. 테스트 파일의 기대값을 수정해 통과시키지 않습니다.
