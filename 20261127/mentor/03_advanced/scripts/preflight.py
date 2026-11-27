"""무료 설정/DB/CUDA 점검. GPU 모델/LLM 추론 성공은 아직 검증하지 않음."""
import json
from app.core.runtime import Runtime
from app.services.errors import ServiceError
def main():
    runtime=None
    try:
        runtime=Runtime();print(json.dumps(runtime.health(),ensure_ascii=False,indent=2));return 0
    except ServiceError as e:
        print(json.dumps(e.envelope(),ensure_ascii=False,indent=2));return 1
    finally:
        if runtime:runtime.close()
if __name__=='__main__':raise SystemExit(main())
