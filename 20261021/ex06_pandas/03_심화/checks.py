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

    def test_clean_rows(self):
        cleaned=target.clean_data(target.make_raw())
        self.assertEqual(len(cleaned),5); self.assertEqual(cleaned["name"].tolist(),["A","B","C","D","E"])
    def test_numeric_missing(self):
        cleaned=target.clean_data(target.make_raw())
        self.assertEqual(int(cleaned["score"].isna().sum()),2)
        self.assertEqual(cleaned["score"].dropna().tolist(),[80.,90.,60.])
    def test_fill_difficulty(self):
        self.assertEqual(target.clean_data(target.make_raw())["difficulty"].tolist(),["기본필수","응용","응용","심화","미정"])
    def test_means(self):
        means=target.group_means(target.clean_data(target.make_raw()))
        self.assertEqual(means.loc["응용"],75.0)
        self.assertTrue(pd.isna(means.loc["심화"])); self.assertTrue(pd.isna(means.loc["미정"]))
    def test_original_preserved(self):
        raw=target.make_raw(); before=raw.copy(deep=True); cleaned=target.clean_data(raw)
        pd.testing.assert_frame_equal(raw,before)
        cleaned.loc[0,"name"]="변경"
        self.assertEqual(raw.loc[0,"name"],"A")
    def test_only_complete_duplicates_removed(self):
        raw=target.make_raw(); extra=raw.iloc[[1]].copy(); extra["score"]="50"
        different=pd.concat([raw,extra],ignore_index=True)
        cleaned=target.clean_data(different)
        self.assertEqual(len(cleaned),6)
        self.assertEqual((cleaned["name"]=="B").sum(),2)

    def test_size_count_mean(self):
        summary=target.group_summary(target.clean_data(target.make_raw()))
        self.assertEqual(summary["difficulty"].tolist(),["기본필수","응용","심화","미정"])
        self.assertEqual(summary["total"].tolist(),[1,2,1,1])
        self.assertEqual(summary["valid"].tolist(),[1,2,0,0])
        self.assertEqual(summary["mean_score"].iloc[:2].tolist(),[80.,75.])
        self.assertTrue(summary["mean_score"].iloc[2:].isna().all())
    def test_audit_values(self):
        raw=target.make_raw(); a=target.audit_changes(raw,target.clean_data(raw))
        self.assertEqual(a,{"before_rows":6,"after_rows":5,"removed_duplicates":1,"original_score_missing":1,"numeric_failures":1,"clean_score_missing":2,"filled_difficulty":1})
    def test_audit_generalized(self):
        raw=target.make_raw().iloc[:2].copy(); raw.loc[1,"score"]="bad"
        a=target.audit_changes(raw,target.clean_data(raw))
        self.assertEqual(a["removed_duplicates"],0); self.assertEqual(a["original_score_missing"],0)
        self.assertEqual(a["numeric_failures"],1); self.assertEqual(a["clean_score_missing"],1)
    def test_empty_typed_frame(self):
        empty=target.make_raw().iloc[:0].copy(); cleaned=target.clean_data(empty)
        summary=target.group_summary(cleaned)
        self.assertTrue(summary.empty); self.assertEqual(summary.columns.tolist(),["difficulty","total","valid","mean_score"])
    def test_json_null_not_nan(self):
        records=target.json_records(target.group_summary(target.clean_data(target.make_raw())))
        encoded=json.dumps(records,ensure_ascii=False,allow_nan=False)
        self.assertIn("null",encoded); self.assertNotIn("NaN",encoded)

if __name__ == "__main__":
    unittest.main(verbosity=2)
