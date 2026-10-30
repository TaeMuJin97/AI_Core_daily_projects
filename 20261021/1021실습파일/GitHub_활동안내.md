# GitHub 변경 이력과 리뷰 활동 · PPT 37~40쪽

수업용 저장소의 URL·접근 권한은 강사가 안내합니다. 이 자료는 GitHub에 자동 접속하거나 커밋/PR을 생성하지 않습니다.
실제 계정이 없거나 접속이 안 되면 아래 오프라인 경로로 같은 학습 목표를 먼저 수행합니다.

## 온라인 활동
1. 강사가 지정한 수업용 저장소에서 작업 목적을 확인합니다. 실제 개인정보·토큰·API 키를 올리지 않습니다.
2. Issue 또는 작업 기록에 “README에 실행 명령과 저장 경로를 추가한다”와 완료 기준을 씁니다.
3. 작업용 브랜치를 만들고 README를 변경합니다. UI의 버튼 위치가 아니라 branch/commit/PR의 역할을 확인합니다.
4. 의미 있는 메시지로 변경을 커밋합니다. 예: `docs: JSON 저장·복원 실행 방법 기록`.
5. diff에서 실행 명령, 경로, 오류 정책만 의도대로 바뀌었는지 확인합니다.
6. 응용은 커밋과 diff 증거를, 심화는 Pull Request와 리뷰 의견·재검증 근거를 남깁니다. 병합은 저장소 담당자가 합니다.

GitHub 웹 편집으로 만든 커밋은 로컬 소스를 자동으로 변경하지 않습니다.
`.gitignore`에 추가해도 이미 추적한 파일이나 유출된 비밀정보가 자동으로 없어지는 것은 아닙니다.
로컬 Git init/add/commit/branch 명령의 본격 실습은 10월 22일 범위입니다.

## 오프라인 대체 활동
해당 실습의 `review/README_before.md`와 `review/README_after.md`를 비교합니다.
역할 폴더에서 다음과 같이 실행합니다(난이도 폴더는 본인의 것으로 바꿉니다).

```text
python tools/compare_readme.py "ex04_json_github/02_응용/review/README_before.md" "ex04_json_github/02_응용/review/README_after.md"
```

본인의 README 변경 전후 파일도 같은 도구로 비교할 수 있습니다.
`협업_활동기록.md`에는 “오프라인 수행, GitHub 미실시”라고 명시합니다. GitHub 완료로 표시하지 않습니다.

## 남길 증거
작업 목적, 변경 파일/줄, diff에서 확인한 내용, 실행 명령, 실제 출력, 리뷰 의견과 반영 결과를 기록합니다.
온라인이면 커밋/PR 식별자 또는 URL을 추가하고, 오프라인이면 비교한 두 파일명과 검토자의 의견을 기록합니다.

## 공식 참고
- GitHub Hello World: https://docs.github.com/en/get-started/start-your-journey/hello-world
- Pull request 검토: https://docs.github.com/en/pull-requests/get-started/reviewing-pull-requests-quickstart
- .gitignore: https://docs.github.com/en/get-started/git-basics/ignoring-files
