"""직접 생성한 모델만 저장·복원합니다. 배포 ZIP에는 joblib 모델을 넣지 않습니다."""
from pathlib import Path
import joblib
import numpy as np
from course_io import sha256,environment

def save_and_verify(selected_models,X_valid,output):
    """{task:fitted_pipeline}을 selected_{task}.joblib로 저장하고 즉시 복원·예측 대조한다.
    반환 dict의 task별 값: file,sha256,predictions_equal. 자기 실행에서 만든 파일만 load한다.
    외부에서 받은 모델 파일은 이 함수에 입력하지 않는다.
    """
    # TODO D6-07-H5: 바로 위 함수 설명의 입력·반환 계약을 완성하세요.
    # raise NotImplementedError("TODO D6-07-H5: 구현 후 다시 실행하세요.")

    output=Path(output); output.mkdir(parents=True, exist_ok=True)
    checks={}
    for task,model in selected_models.items():
        path=output/f'selected_{task}.joblib'
        before=model.predict(X_valid)
        joblib.dump(model,path)
        restored=joblib.load(path) # 위에서 지금 생성한 신뢰 가능한 파일만 읽습니다.
        after=restored.predict(X_valid)
        equal=bool.(np.allclose(before,after,rtol=1e-12))
        if not equal: raise AssertionError('저장 전후 예측이 다릅니다.')
        checks[task]={'file':path.name, 'sha256':sha256(path),'predictions_equal' : equal}
    return checks