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

import pandas as pd
import main as target
class PandasTests(unittest.TestCase):
    def test_input_shape(self): self.assertEqual(target.make_raw().shape,(6,4))
    def test_columns(self): self.assertEqual(target.make_raw().columns.tolist(),["name","difficulty","score","role_count"])
    def test_raw_values(self):
        raw=target.make_raw(); self.assertEqual(raw["name"].tolist(),["A","B","B","C","D","E"])
        self.assertEqual(raw.iloc[4]["score"],"미정")
        self.assertTrue(pd.isna(raw.iloc[5]["score"]))
    def test_selection_before_dedup(self):
        raw=target.make_raw(); before=raw.copy(deep=True)
        self.assertEqual(target.select_applied(raw),["B","B","C"])
        pd.testing.assert_frame_equal(raw,before)
    def test_selection_general_input(self):
        raw=pd.DataFrame({"name":["X","Y"],"difficulty":["응용","심화"]})
        self.assertEqual(target.select_applied(raw),["X"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
