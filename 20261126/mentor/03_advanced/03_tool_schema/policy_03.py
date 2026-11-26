"""경계값·오류/권한 정책: Advanced · Day29."""

def schema_fields(tool_obj) -> list[str]:
    """모델에게 노출되는 Tool 입력 필드 이름을 목록으로 반환합니다."""
    # 해설 D29-03-A-03: 모델에게 노출될 인수 Schema와 실제 Python Tool의 실행을 별도 관찰합니다.
    # 검수 기준: report_id는 실제 DB의 양의 정수이며 task_id가 아닙니다.
    schema=tool_obj.args_schema.model_json_schema()
    return sorted(schema.get('properties',{}))

def enforce_explicit_schema(tool_obj) -> dict:
    """Tool JSON Schema에 report_id가 required인지 점검합니다."""
    # 해설 D29-03-A-04: 모델에게 노출될 인수 Schema와 실제 Python Tool의 실행을 별도 관찰합니다.
    # 검수 기준: report_id는 실제 DB의 양의 정수이며 task_id가 아닙니다.
    schema=tool_obj.args_schema.model_json_schema()
    if 'report_id' not in schema.get('required',[]):raise ValueError('report_id 필수 인수 누락')
    return {'name':tool_obj.name,'required':schema['required']}

