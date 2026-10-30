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

import main as target
class ClassTests(unittest.TestCase):
    def test_fields(self):
        a=target.Idea(" 문서 ", " 검색 ", ["R"], "응용")
        self.assertEqual((a.name,a.problem,a.difficulty),("문서","검색","응용"))
    def test_two_summaries(self):
        a=target.Idea("문서", "검색", ["R","W"], "응용")
        b=target.Idea("학습", "복습", ["T"], "기본필수")
        self.assertEqual(a.summary(), "문서: 역할 2개")
        self.assertEqual(b.summary(), "학습: 역할 1개")
    def test_input_copy(self):
        roles=["R"]
        a=target.Idea("문서", "검색", roles, "응용")
        roles.append("W")
        self.assertEqual(a.roles,["R"])
        self.assertIsNot(a.roles,roles)
    def test_objects_are_independent(self):
        roles=["R"]
        a=target.Idea("문서", "검색", roles, "응용")
        b=target.Idea("학습", "복습", roles, "기본필수")
        a.roles.append("W")
        self.assertEqual(b.roles,["R"])
    def test_summary_returns_without_print(self):
        a=target.Idea("문서", "검색", ["R"], "응용")
        output=io.StringIO()
        with redirect_stdout(output): value=a.summary()
        self.assertIsInstance(value,str)
        self.assertEqual(output.getvalue(),"")
    def test_import_is_quiet(self):
        result=subprocess.run([sys.executable,"-B","-c","import main"],cwd=HERE,capture_output=True,text=True,encoding="utf-8",timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,"")

    def test_add_new(self):
        a=target.Idea("문서","검색",["R"],"응용")
        self.assertIs(a.add_role(" Writer "),True)
        self.assertEqual(a.roles,["R","Writer"])
    def test_duplicate_no_change(self):
        a=target.Idea("문서","검색",["Writer"],"응용")
        self.assertIs(a.add_role(" writer "),False)
        self.assertEqual(a.roles,["Writer"])
    def test_empty_invalid(self):
        a=target.Idea("문서","검색",["R"],"응용")
        for value in ("", "  ", None, 3):
            with self.subTest(value=value),self.assertRaises(ValueError): a.add_role(value)
        self.assertEqual(a.roles,["R"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
