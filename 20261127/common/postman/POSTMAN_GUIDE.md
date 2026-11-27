# Postman · Day30
1. Collection/Environment JSON 2개를 Import하고 Day30 local Environment를 선택합니다.
2. 프로젝트에서 `python -m app.main` 실행. /docs와 /health 먼저 확인합니다.
3. `project_level`을 선택한 난이도로 설정합니다. `report_id`는 실제 존재하고 유효한 벡터가 있는 ID, `missing_report_id`는 실제 없는 ID인지 SQL로 확인하세요.
4. 무료 폴더 01부터 실행합니다. 입력 검증 422는 LLM을 호출하지 않습니다. DB/GPU 미준비 시 /health 503을 수정합니다.
5. 실제 API 비용·키·모델을 확인한 뒤 `allow_paid_llm=true`로 바꾸고 폴더 02를 실행합니다. 사용 후 false로 복원합니다. 응용/심화 debug도 Rewrite가 유료입니다. Collection Runner 또는 개별 요청에서 skipRequest가 지원되는 최신 Postman을 사용하세요. 미지원 버전에서는 유료 폴더를 직접 실행하지 마세요.
6. 복합 요청에서 `rag_search`, `lookup_status` ToolMessage가 실제 실행되었는지 확인합니다. status-only 질문은 두 Tool을 강제하지 않습니다. 응답의 sources는 직접 Context와 원문을 대조하세요. 모든 테스트가 HTTP 200만 검사하는 것이 아닙니다.
7. Advanced는 최근 request_id가 설정되어 있으면 API-03 실행. 서버 재시작 후 404가 정상입니다.
8. 실제 결과/실패를 제출 checklist에 기록합니다. API 키·DB 비밀번호는 Environment에 넣지 않습니다. 503/504는 정상 실패 처리인지 확인하세요.
