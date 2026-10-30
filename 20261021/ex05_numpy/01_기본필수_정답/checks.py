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

import numpy as np
import main as target
class NumpyTests(unittest.TestCase):
    def test_shape_dtype(self):
        a=target.make_latency(); self.assertEqual(a.shape,(3,2)); self.assertEqual(a.ndim,2)
        self.assertTrue(np.issubdtype(a.dtype,np.floating))
    def test_values(self):
        np.testing.assert_array_equal(target.make_latency(),[[100,200],[150,250],[200,300]])
    def test_mean_max(self):
        r=target.basic_stats(target.make_latency())
        self.assertEqual(r["shape"],[3,2]); self.assertAlmostEqual(r["mean_ms"],200); self.assertEqual(r["max_ms"],300)
    def test_seconds(self):
        r=target.basic_stats(target.make_latency())
        np.testing.assert_allclose(r["seconds"],[[.1,.2],[.15,.25],[.2,.3]])
    def test_source_not_modified(self):
        a=target.make_latency(); before=a.copy(); target.basic_stats(a)
        np.testing.assert_array_equal(a,before)
    def test_other_values_not_hardcoded(self):
        r=target.basic_stats(np.array([[10.,30.],[50.,70.]]))
        self.assertEqual(r["mean_ms"],40); self.assertEqual(r["max_ms"],70)
    def test_empty_rejected(self):
        with self.assertRaises(ValueError): target.basic_stats(np.empty((0,2)))

if __name__ == "__main__":
    unittest.main(verbosity=2)
