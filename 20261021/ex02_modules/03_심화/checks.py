"""공개 확인 테스트. 구현 예시가 아니라 입력·출력 계약을 확인합니다."""
import unittest
import tempfile
import subprocess
import sys
import os
import json
import copy
import io
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch
HERE = Path(__file__).resolve().parent
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

PROJECT = HERE / "day3_console"
sys.path.insert(0, str(PROJECT))  # 검사 도구가 검사할 패키지 루트를 지정
from idea_app.models import Idea
from idea_app.service import IdeaCatalog
class ModuleTests(unittest.TestCase):
    def test_package_layout(self):
        for name in ("__init__.py","models.py","main.py","service.py"):
            self.assertTrue((PROJECT/"idea_app"/name).is_file())
    def test_module_command(self):
        p=subprocess.run([sys.executable,"-B","-m","idea_app.main"],cwd=PROJECT,capture_output=True,text=True,encoding="utf-8",timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("['문서', '학습']",p.stdout)
    def test_import_no_io(self):
        command="from unittest.mock import patch; from contextlib import ExitStack; import builtins; import pathlib; stack=ExitStack(); stack.enter_context(patch('builtins.input',side_effect=AssertionError('input 부작용'))); stack.enter_context(patch.object(pathlib.Path,'write_text',side_effect=AssertionError('쓰기 부작용'))); import idea_app.main; import idea_app.service; import idea_app.models"
        p=subprocess.run([sys.executable,"-B","-c",command],cwd=PROJECT,capture_output=True,text=True,encoding="utf-8",timeout=10)
        self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(p.stdout,"")
        self.assertFalse((PROJECT/"data").exists())
    def test_catalog(self):
        c=IdeaCatalog(); c.add(Idea("문서","검색",["R"],"응용"))
        self.assertEqual(c.names(),["문서"])
    def test_service_no_print(self):
        out=io.StringIO()
        with redirect_stdout(out):
            c=IdeaCatalog(); c.add(Idea("문서","검색",["R"],"응용")); c.names()
        self.assertEqual(out.getvalue(),"")
    def test_catalog_state(self):
        a,b=IdeaCatalog(),IdeaCatalog(); a.add(Idea("문서","검색",["R"],"응용"))
        self.assertEqual(b.names(),[])

    def test_roles(self):
        from idea_app.agents import Researcher, Writer, run_roles
        self.assertEqual(run_roles([Researcher(),Writer()],"Python"),["검색: Python","작성: Python"])
    def test_substitutability(self):
        from idea_app.agents import run_roles
        class Reviewer:
            def run(self,task): return f"검토: {task}"
        self.assertEqual(run_roles([Reviewer()],"문서"),["검토: 문서"])
    def test_base_contract(self):
        from idea_app.agents import Agent
        with self.assertRaises(NotImplementedError): Agent().run("Python")

if __name__ == "__main__":
    unittest.main(verbosity=2)
