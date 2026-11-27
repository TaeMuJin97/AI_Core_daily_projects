"""공통 설정/평가자료/단계별 검증 복사만 수행. 사용 예: python common/prepare_project.py mentee/02_intermediate"""
from pathlib import Path
import argparse,shutil
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('project');a=p.parse_args();target=Path(a.project).resolve()
if not target.is_dir():p.error('선택한 프로젝트 폴더가 존재해야 합니다.')
files=['requirements.txt','.env.example','.gitignore','pytest.ini']
# 제공된 검증 파일만 복사한다. 캐시·사용자가 생성한 파일은 제외.
files += ['test/'+p.name for p in sorted((HERE/'test').iterdir()) if p.is_file() and (p.suffix=='.py' or p.name=='README.md')]
if target.name!='01_basic':files += ['data/evaluation/gold.json','data/evaluation/README.md','data/evaluation/human_review.csv']
for name in files:
    dest=target/name
    if dest.exists():print('skip existing:',name);continue
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/name,dest);print('copied:',name)
print('DB, 업무 Python 소스, 기존 .env는 변경하지 않았습니다. 단계별 검증 test/는 공통 제공 파일입니다.')
