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
class FileTests(unittest.TestCase):
    def test_valid_count(self):
        self.assertEqual(target.parse_count("2"),2)
        self.assertEqual(target.parse_count(" 3 "),3)
    def test_noninteger(self):
        for raw in ("abc","1.5",""):
            with self.subTest(raw=raw),self.assertRaises(ValueError): target.parse_count(raw)
    def test_nonpositive(self):
        for raw in ("0","-1"):
            with self.subTest(raw=raw),self.assertRaises(ValueError): target.parse_count(raw)
    def test_utf8_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"하위 폴더"/"note.txt"; text="한글·AI\n"
            target.save_note(p,text)
            self.assertEqual(target.read_note(p),text)
            self.assertEqual(p.read_bytes(),text.encode("utf-8"))
    def test_read_only_no_change(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"note.txt"; p.write_text("원본",encoding="utf-8"); before=p.read_bytes()
            target.read_note(p); self.assertEqual(p.read_bytes(),before)
    def test_expected_path(self):
        self.assertEqual(target.note_path(),HERE/"data"/"note.txt")

if __name__ == "__main__":
    unittest.main(verbosity=2)
