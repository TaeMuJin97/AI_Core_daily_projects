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
sys.path.insert(0,str(PROJECT))  # 테스트에서만 대상 패키지를 찾는 설정
from idea_app.models import Idea, from_record, to_record
from idea_app.service import IdeaCatalog
from idea_app import storage, io_support, analytics
from idea_app.main import reload_catalog
class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.workspace=Path(self.temp.name); self.path=self.workspace/"data"/"ideas.json"
        self.records=json.loads((PROJECT/"fixtures"/"valid_ideas.json").read_text(encoding="utf-8"))
    def run_cli(self, args=(), text=None):
        return subprocess.run([sys.executable,"-B","-X","utf8","-m","idea_app.main","--workspace",str(self.workspace),*args],cwd=PROJECT,input=text,capture_output=True,text=True,encoding="utf-8",timeout=20)
    def test_add_list(self):
        c=IdeaCatalog()
        for r in self.records[:2]: c.add(from_record(r))
        self.assertEqual(c.names(),["문서 도우미","학습 도우미"])
    def test_all_required_fields(self):
        for key,value in (("name"," "),("problem",""),("roles",[]),("difficulty","미정")):
            r=copy.deepcopy(self.records[0]); r[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError): from_record(r)
    def test_bad_role_values(self):
        for roles in ([" "],"Writer",[3],["Writer"," writer "]):
            with self.subTest(roles=roles),self.assertRaises(ValueError): Idea("문서","검색",roles,"응용")
    def test_role_copy(self):
        roles=["R"]; first=Idea("A","p",roles,"응용"); second=Idea("B","p",roles,"응용")
        first.roles.append("W"); roles.append("P")
        self.assertEqual(second.roles,["R"])
    def test_catalog_instances(self):
        a,b=IdeaCatalog(),IdeaCatalog(); a.add(from_record(self.records[0])); self.assertEqual(b.names(),[])
    def test_list_copy_container(self):
        c=IdeaCatalog(); c.add(from_record(self.records[0])); copied=c.list_all(); copied.clear()
        self.assertEqual(len(c.list_all()),1)
    def test_first_run_missing(self):
        c=IdeaCatalog(); reload_catalog(c,self.path); self.assertEqual(c.names(),[])
        self.assertFalse(self.path.exists())
    def test_save_restore(self):
        storage.save_records(self.path,self.records)
        c=IdeaCatalog(); reload_catalog(c,self.path)
        self.assertEqual([to_record(i) for i in c.list_all()],self.records)
    def test_demo_then_new_process(self):
        p=self.run_cli(["--demo"]); self.assertEqual(p.returncode,0,p.stderr+p.stdout)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")),self.records)
        self.assertTrue((self.workspace/"reports"/"summary.txt").is_file())
        q=self.run_cli(["--show"]); self.assertEqual(q.returncode,0,q.stderr)
        for r in self.records: self.assertIn(r["name"],q.stdout)
    def test_demo_never_overwrites(self):
        self.path.parent.mkdir(parents=True); self.path.write_text("keep",encoding="utf-8")
        p=self.run_cli(["--demo"]); self.assertEqual(p.returncode,2)
        self.assertEqual(self.path.read_text(encoding="utf-8"),"keep")
    def test_interactive_register_save_restart(self):
        lines="1\n문서 도우미\n자료 검색 시간을 줄인다\nResearcher, Writer\n응용\n2\n5\n0\n"
        p=self.run_cli(text=lines); self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("아이디어 등록 완료",p.stdout); self.assertIn("저장 완료",p.stdout)
        self.assertEqual(len(json.loads(self.path.read_text(encoding="utf-8"))),1)
        self.assertIn("문서 도우미",self.run_cli(["--show"]).stdout)
    def test_bad_input_does_not_add(self):
        lines="1\n  \n문제\nWriter\n응용\n2\n0\n"
        p=self.run_cli(text=lines); self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("등록 거부",p.stdout); self.assertIn("등록된 아이디어가 없습니다",p.stdout)
    def test_eof_exits_no_autosave(self):
        p=self.run_cli(text=""); self.assertEqual(p.returncode,0,p.stderr)
        self.assertFalse(self.path.exists())
    def test_no_autosave_on_quit(self):
        p=self.run_cli(text="1\nA\np\nR\n응용\n0\n")
        self.assertEqual(p.returncode,0,p.stderr); self.assertFalse(self.path.exists())
        self.assertIn("저장하지 않은 변경",p.stdout)
    def test_failed_save_keeps_file_and_memory(self):
        storage.save_records(self.path,self.records); before=self.path.read_bytes(); records=copy.deepcopy(self.records)
        with patch.object(io_support.os,"replace",side_effect=PermissionError("교육용")):
            with self.assertRaises(PermissionError): storage.save_records(self.path,records)
        self.assertEqual(self.path.read_bytes(),before); self.assertEqual(records,self.records)
    def test_import_no_interaction(self):
        script="from unittest.mock import patch; guard=patch('builtins.input',side_effect=AssertionError('input')); guard.start(); import idea_app.main, idea_app.service, idea_app.storage, idea_app.analytics"
        p=subprocess.run([sys.executable,"-B","-c",script],cwd=PROJECT,capture_output=True,text=True,encoding="utf-8",timeout=10)
        self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(p.stdout,"")
    def test_absolute_launcher_from_outside(self):
        p=subprocess.run([sys.executable,"-B",str(PROJECT/"run_console.py"),"--workspace",str(self.workspace),"--show"],cwd=self.workspace,capture_output=True,text=True,encoding="utf-8",timeout=10)
        self.assertEqual(p.returncode,0,p.stderr); self.assertFalse(self.path.exists())
    def test_corrupt_startup_write_blocked(self):
        self.path.parent.mkdir(parents=True); self.path.write_text("[{bad]",encoding="utf-8"); before=self.path.read_bytes()
        p=self.run_cli(text="5\n0\n"); self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("저장 차단",p.stdout); self.assertNotIn("저장 완료",p.stdout)
        self.assertEqual(self.path.read_bytes(),before)

    def test_duplicate_rejection(self):
        c=IdeaCatalog(); c.add(Idea(" Alpha ","p",["R"],"응용"))
        with self.assertRaises(ValueError): c.add(Idea("alpha","q",["W"],"심화"))
        self.assertEqual(c.names(),["Alpha"])
    def test_search(self):
        c=IdeaCatalog()
        for r in self.records: c.add(from_record(r))
        self.assertEqual([i.name for i in c.search(" 복습 ")],["학습 도우미"])
        self.assertEqual(c.search("없는키워드"),[])
        with self.assertRaises(ValueError): c.search(" ")
    def test_numpy_roles(self):
        r=analytics.summarize_roles([from_record(x) for x in self.records])
        self.assertEqual(r,{"count":3,"mean":2.0,"max":3})
    def test_empty_role_stats(self):
        self.assertEqual(analytics.summarize_roles([]),{"count":0,"mean":None,"max":None})
    def test_pandas_summary(self):
        frame=analytics.summarize_difficulty([from_record(x) for x in self.records])
        self.assertEqual(frame["difficulty"].tolist(),["기본필수","응용","심화"])
        self.assertEqual(frame["count"].tolist(),[1,1,1])
    def test_missing_categories_zero(self):
        frame=analytics.summarize_difficulty([from_record(self.records[0])])
        self.assertEqual(frame["count"].tolist(),[0,1,0])
        self.assertEqual(analytics.summarize_difficulty([])["count"].tolist(),[0,0,0])
    def test_analytics_no_mutation(self):
        ideas=[from_record(x) for x in self.records]; before=[to_record(i) for i in ideas]
        analytics.summarize_roles(ideas); analytics.summarize_difficulty(ideas)
        self.assertEqual([to_record(i) for i in ideas],before)

    def test_all_invalid_fixture_cases(self):
        for name in ("broken.json","missing_key.json","wrong_top_level.json","wrong_roles_type.json","duplicate_names.json","duplicate_roles.json"):
            c=IdeaCatalog(); old=from_record(self.records[0]); c.add(old)
            p=PROJECT/"fixtures"/name; before=p.read_bytes()
            with self.subTest(file=name),self.assertRaises(ValueError): reload_catalog(c,p)
            self.assertEqual(c.names(),[old.name]); self.assertIs(c.list_all()[0],old)
            self.assertEqual(p.read_bytes(),before)
    def test_partial_record_never_applied(self):
        c=IdeaCatalog(); old=from_record(self.records[0]); c.add(old)
        self.path.parent.mkdir(parents=True); self.path.write_text(json.dumps([self.records[1],{"name":"bad"}],ensure_ascii=False),encoding="utf-8")
        with self.assertRaises(ValueError): reload_catalog(c,self.path)
        self.assertIs(c.list_all()[0],old)
    def test_replace_all_is_transactional(self):
        c=IdeaCatalog(); old=from_record(self.records[0]); c.add(old)
        with self.assertRaises(ValueError): c.replace_all([from_record(self.records[1]),from_record(self.records[1])])
        self.assertIs(c.list_all()[0],old)
    def test_save_validation_precedes_touching_file(self):
        storage.save_records(self.path,self.records); before=self.path.read_bytes()
        with self.assertRaises(ValueError): storage.save_records(self.path,[{"name":"bad"}])
        self.assertEqual(self.path.read_bytes(),before)
    def test_error_reports_index(self):
        with self.assertRaisesRegex(ValueError,"레코드 2"):
            storage.validate_records([self.records[0],{"name":"bad"}])
    def test_mock_permission_reload_preserves(self):
        c=IdeaCatalog(); old=from_record(self.records[0]); c.add(old)
        with patch.object(Path,"open",side_effect=PermissionError("교육용")):
            with self.assertRaises(PermissionError): reload_catalog(c,self.path)
        self.assertIs(c.list_all()[0],old)

# 이 클래스의 3개 테스트는 수강생이 test_cases.py에서 직접 완성합니다.
from test_cases import SafetyEvidenceTests

if __name__ == "__main__":
    unittest.main(verbosity=2)
