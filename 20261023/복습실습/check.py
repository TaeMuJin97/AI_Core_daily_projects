"""학습 확인 도구(수정 불필요). 예: python check.py 01_basic / python check.py 04_basic
완료는 수치 검사가 통과했다는 뜻입니다. 이해·설명·코드 품질을 자동 채점하지 않습니다.
"""
from pathlib import Path
import copy
import importlib.util
import io
import contextlib
import json
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


def load(folder, stem):
    """학습 파일을 읽되, main은 실행하지 않습니다."""
    parent = BASE / folder
    # 같은 이름의 제공 모듈이 다른 단원에서 남아 있지 않도록 다시 읽습니다.
    for name in ("storage", "validation", "models", "cleaning", "reporting"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(parent))
    try:
        spec = importlib.util.spec_from_file_location("review_" + folder + "_" + stem, parent / (stem + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def fixture(mode="basic"):
    st = load("03_files", "storage")
    data = BASE / "03_files/data"
    return st.read_csv(data / ("orders_" + mode + ".csv")) + st.read_json(data / ("orders_" + mode + ".json"))


def expected_rows():
    # 프로그램에서 답을 가져오는 대신 손으로 확인한 5행을 기준으로 씁니다.
    return [
        {"order_id": "C01", "item": "아메리카노", "unit_price": 3000, "quantity": 2, "amount": 6000},
        {"order_id": "C02", "item": "카페라떼", "unit_price": 4000, "quantity": 1, "amount": 4000},
        {"order_id": "C03", "item": "쿠키", "unit_price": 2000, "quantity": 3, "amount": 6000},
        {"order_id": "J01", "item": "아메리카노", "unit_price": 3000, "quantity": 1, "amount": 3000},
        {"order_id": "J02", "item": "카페라떼", "unit_price": 4000, "quantity": 2, "amount": 8000},
    ]


def expected_groups():
    return {"아메리카노": {"quantity": 3, "amount": 9000},
            "카페라떼": {"quantity": 3, "amount": 12000},
            "쿠키": {"quantity": 3, "amount": 6000}}


class FunctionBasic(unittest.TestCase):
    def setUp(self): self.m = load("01_functions", "basic")
    def test_amount(self):
        self.assertEqual(self.m.calculate_amount(3000, 2), 6000)
        self.assertEqual(self.m.calculate_amount(4000, 1), 4000)
    def test_return_not_print(self):
        screen = io.StringIO()
        with contextlib.redirect_stdout(screen): value = self.m.calculate_amount(2000, 3)
        self.assertEqual(value, 6000)
        self.assertEqual(screen.getvalue(), "", "계산 함수는 print가 아니라 return을 사용합니다.")
    def test_message(self): self.assertEqual(self.m.receipt_message("쿠키", 6000), "쿠키: 6000원")
    def test_composition(self): self.assertEqual(self.m.describe_order("카페라떼", 4000, 2), "카페라떼: 8000원")


class FunctionApplied(unittest.TestCase):
    def setUp(self): self.m = load("01_functions", "applied")
    def test_total(self): self.assertEqual(self.m.total_amount(expected_rows()[:3]), 16000)
    def test_empty(self): self.assertEqual(self.m.total_amount([]), 0)
    def test_boundary(self): self.assertEqual(self.m.count_large_orders(expected_rows()[:3], 6000), 2)
    def test_no_change(self):
        rows = expected_rows(); before = copy.deepcopy(rows)
        self.m.total_amount(rows); self.assertEqual(rows, before)


class FunctionAdvanced(unittest.TestCase):
    def setUp(self): self.m = load("01_functions", "advanced")
    def test_valid(self):
        for value in (2, "2", " 2 ", "+2"): self.assertEqual(self.m.parse_quantity(value), 2)
    def test_invalid(self):
        for value in ("", "두 개", "2.5", -1, 0, None, 2.0, True): self.assertIsNone(self.m.parse_quantity(value))
    def test_summary(self): self.assertEqual(self.m.summarize_quantities(["2", " 3 ", "", "두 개", "-1", 0, None, 1.5, True]), (5, 7))
    def test_empty(self): self.assertEqual(self.m.summarize_quantities([]), (0, 0))


class ClassBasic(unittest.TestCase):
    def setUp(self): self.m = load("02_classes", "basic")
    def test_attributes(self):
        order = self.m.Order("쿠키", 2000, 3)
        self.assertEqual((order.item, order.unit_price, order.quantity), ("쿠키", 2000, 3))
    def test_method(self): self.assertEqual(self.m.Order("쿠키", 2000, 3).amount(), 6000)
    def test_independent(self):
        a = self.m.Order("아메리카노", 3000, 2); b = self.m.Order("카페라떼", 4000, 1)
        a.quantity = 3
        self.assertEqual((a.amount(), b.amount()), (9000, 4000))


class ClassApplied(unittest.TestCase):
    def setUp(self): self.m = load("02_classes", "applied")
    def test_change(self):
        obj = self.m.Order("쿠키", 2000, 3); obj.set_quantity(4); self.assertEqual(obj.amount(), 8000)
    def test_bad_change_keeps_old(self):
        obj = self.m.Order("쿠키", 2000, 3)
        for bad in (0, -2, "2", 1.5, True):
            with self.assertRaises(ValueError): obj.set_quantity(bad)
            self.assertEqual(obj.quantity, 3)
    def test_dictionary(self):
        self.assertEqual(self.m.Order("쿠키", 2000, 3).to_dict(), {"item":"쿠키", "unit_price":2000, "quantity":3, "amount":6000})
    def test_new_dictionary(self):
        obj = self.m.Order("쿠키", 2000, 3); result = obj.to_dict(); result["quantity"] = 99
        self.assertEqual(obj.quantity, 3)


class ClassAdvanced(unittest.TestCase):
    def setUp(self): self.m = load("02_classes", "advanced")
    def test_empty(self): self.assertEqual(self.m.Cart().total_amount(), 0)
    def test_total(self):
        cart = self.m.Cart(); cart.add(self.m.Order("아메리카노", 3000, 2)); cart.add(self.m.Order("쿠키", 2000, 3))
        self.assertEqual(cart.total_amount(), 12000)
    def test_no_shared_list(self):
        a = self.m.Cart(); b = self.m.Cart(); a.add(self.m.Order("쿠키", 2000, 1))
        self.assertEqual(b.total_amount(), 0); self.assertIsNot(a.orders, b.orders)
    def test_object_reference(self):
        cart = self.m.Cart(); order = self.m.Order("쿠키", 2000, 1); cart.add(order); order.quantity = 2
        self.assertEqual(cart.total_amount(), 4000)


class FileBasic(unittest.TestCase):
    def setUp(self): self.m = load("03_files", "basic")
    def test_loading(self):
        rows = self.m.load_orders(BASE / "03_files/data/orders_basic.csv", BASE / "03_files/data/orders_basic.json")
        self.assertEqual(len(rows), 5); self.assertEqual(rows[3]["order_id"], "J01")
    def test_clean_rows(self): self.assertEqual([self.m.clean_one(r) for r in fixture()], expected_rows())
    def test_no_mutation(self):
        row = fixture()[0]; old = row.copy(); self.m.clean_one(row); self.assertEqual(row, old)
    def test_summary(self): self.assertEqual(self.m.make_summary(expected_rows()), {"order_count":5,"total_quantity":9,"total_amount":27000})
    def test_empty(self): self.assertEqual(self.m.make_summary([]), {"order_count":0,"total_quantity":0,"total_amount":0})


class FileApplied(unittest.TestCase):
    def setUp(self): self.m = load("03_files", "applied")
    def test_filter(self):
        clean, rejected = self.m.clean_with_reasons(fixture("applied"))
        self.assertEqual(clean, expected_rows()); self.assertEqual(len(rejected), 5)
        self.assertEqual([r["record_no"] for r in rejected], [4,5,6,7,8])
    def test_reasons(self):
        clean, rejected = self.m.clean_with_reasons(fixture("applied"))
        self.assertEqual([r["reason"] for r in rejected], ["수량 오류"]*3+["상품명 누락","단가 오류"])
        self.assertEqual(rejected[0]["raw"]["quantity"], "")
    def test_groups(self): self.assertEqual(self.m.group_by_item(expected_rows()), expected_groups())
    def test_empty(self):
        self.assertEqual(self.m.clean_with_reasons([]), ([], [])); self.assertEqual(self.m.group_by_item([]), {})
    def test_original(self):
        rows = fixture("applied"); old = copy.deepcopy(rows); self.m.clean_with_reasons(rows); self.assertEqual(rows, old)


class FileAdvanced(unittest.TestCase):
    def setUp(self): self.m = load("03_files", "advanced")
    def test_counts(self):
        clean, rejected = self.m.clean_unique(fixture("advanced"))
        self.assertEqual((len(clean),len(rejected)),(6,8)); self.assertEqual(sum(r["amount"] for r in clean),31000)
    def test_duplicate_keeps_first(self):
        rows = expected_rows()[:1] + [dict(expected_rows()[0], quantity=9)]
        clean, rejected = self.m.clean_unique(rows)
        self.assertEqual(clean[0]["quantity"],2); self.assertEqual(rejected[0]["reason"],"중복 ID: 확인 필요")
    def test_bad_first_not_seen(self):
        rows = [dict(expected_rows()[0], quantity="")] + expected_rows()[:1]
        clean, rejected = self.m.clean_unique(rows)
        self.assertEqual((len(clean),len(rejected)),(1,1)); self.assertEqual(clean[0]["quantity"],2)
    def test_reason_counts(self):
        clean, rejected = self.m.clean_unique(fixture("advanced"))
        self.assertEqual(self.m.count_reasons(rejected),{"수량 오류":4,"상품명 누락":1,"단가 오류":1,"중복 ID: 확인 필요":2})
    def test_empty(self):
        self.assertEqual(self.m.clean_unique([]),([],[])); self.assertEqual(self.m.count_reasons([]),{})


class ProjectBasic(unittest.TestCase):
    def setUp(self): self.m = load("04_project", "main")
    def test_clean(self): self.assertEqual(self.m.clean_orders(fixture()),expected_rows())
    def test_objects(self):
        orders = self.m.make_orders(expected_rows()); self.assertEqual(len(orders),5)
        self.assertEqual(orders[0].amount(),6000); self.assertEqual(orders[4].item,"카페라떼")
    def test_summary(self):
        self.assertEqual(self.m.summarize_orders(self.m.make_orders(expected_rows())),{"order_count":5,"total_quantity":9,"total_amount":27000})
    def test_pipeline(self):
        result = self.m.run("basic")
        self.assertEqual(result,{"order_count":5,"total_quantity":9,"total_amount":27000,"raw_count":5,"rejected_count":0})
        with (BASE/"04_project/outputs/basic/summary.json").open(encoding="utf-8") as f:
            self.assertEqual(json.load(f),result)
    def test_empty(self): self.assertEqual(self.m.summarize_orders(self.m.make_orders([])),{"order_count":0,"total_quantity":0,"total_amount":0})


class ProjectApplied(unittest.TestCase):
    def setUp(self): self.m = load("04_project", "main")
    def test_groups(self): self.assertEqual(self.m.group_orders(self.m.make_orders(expected_rows())),expected_groups())
    def test_pipeline(self):
        result=self.m.run("applied"); self.assertEqual(result["by_item"],expected_groups());self.assertEqual(result["total_amount"],27000)
    def test_empty_group(self): self.assertEqual(self.m.group_orders([]),{})


class ProjectAdvanced(unittest.TestCase):
    def setUp(self): self.m = load("04_project", "main")
    def test_clean(self):
        clean,rejected=self.m.clean_orders_advanced(fixture("advanced"));self.assertEqual((len(clean),len(rejected)),(6,8))
    def test_pipeline(self):
        result=self.m.run("advanced")
        self.assertEqual((result["raw_count"],result["order_count"],result["rejected_count"],result["total_quantity"],result["total_amount"]),(14,6,8,11,31000))
        self.assertEqual(result["by_item"]["쿠키"],{"quantity":5,"amount":10000})
    def test_invalid_mode(self):
        with self.assertRaises(ValueError): self.m.run("bad")
    def test_empty(self): self.assertEqual(self.m.clean_orders_advanced([]),([],[]))


class ProvidedTools(unittest.TestCase):
    """이 검사는 제공 코드용입니다. 수강생 구현 여부를 판단하는 데 사용하지 않습니다."""
    def setUp(self): self.m=load("03_files","storage"); self.v=load("03_files","validation")
    def test_header_only(self): self.assertEqual(self.m.read_csv(BASE/"03_files/data/empty.csv"),[])
    def test_empty_json(self): self.assertEqual(self.m.read_json(BASE/"03_files/data/empty.json"),[])
    def test_bad_json(self):
        with self.assertRaises(json.JSONDecodeError): self.m.read_json(BASE/"03_files/data/broken.json")
    def test_bad_structure(self):
        with self.assertRaises(ValueError): self.m.read_json(BASE/"03_files/data/wrong_structure.json")
    def test_missing_column(self):
        with self.assertRaises(ValueError): self.m.read_csv(BASE/"03_files/data/missing_column.csv")
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError): self.m.read_csv(BASE/"03_files/data/not_a_file.csv")
    def test_roundtrip_empty(self):
        with tempfile.TemporaryDirectory() as d: self.assertTrue(self.m.save_results(Path(d),[],{"count":0},[]))
    def test_roundtrip_leading_zero(self):
        rows=[dict(expected_rows()[0],order_id="001")]
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(self.m.save_results(Path(d),rows,{"count":1}))
            self.assertEqual(self.m.read_csv(Path(d)/"clean_orders.csv")[0]["order_id"],"001")
    def test_read_does_not_change_file(self):
        path=BASE/"03_files/data/orders_basic.csv"; old=path.read_bytes();self.m.read_csv(path);self.assertEqual(path.read_bytes(),old)
    def test_validation(self):
        for value in (True,1.5,"",None,"-1","0","3,000"): self.assertIsNone(self.v.positive_int(value))
        self.assertEqual(self.v.positive_int(" 2 "),2)
    def test_missing_id(self): self.assertEqual(self.v.check_row({"item":"쿠키"})[1],"ID 누락")


GROUPS = {
    "01_basic":FunctionBasic,"01_applied":FunctionApplied,"01_advanced":FunctionAdvanced,
    "02_basic":ClassBasic,"02_applied":ClassApplied,"02_advanced":ClassAdvanced,
    "03_basic":FileBasic,"03_applied":FileApplied,"03_advanced":FileAdvanced,
    "04_basic":ProjectBasic,"04_applied":ProjectApplied,"04_advanced":ProjectAdvanced,
    "provided":ProvidedTools,
}


class LearningResult(unittest.TextTestResult):
    def addError(self,test,err):
        if issubclass(err[0],NotImplementedError):
            self.addSkip(test,"미완성: "+str(err[1]))
        else:
            super().addError(test,err)


def main():
    key=sys.argv[1] if len(sys.argv)>1 else "help"
    if key=="help":
        print("사용법: python check.py 01_basic")
        print("확인할 단원:",", ".join(GROUPS))
        print("강사용 전체 검사: python check.py all")
        return 0
    if key not in GROUPS and key!="all":
        print("알 수 없는 단원입니다. python check.py로 목록을 확인하세요.");return 1
    suite=unittest.TestSuite()
    classes=GROUPS.values() if key=="all" else [GROUPS[key]]
    for cls in classes: suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    runner=unittest.TextTestRunner(verbosity=2,resultclass=LearningResult,stream=sys.stdout)
    result=runner.run(suite)
    pending=len(result.skipped); problems=len(result.failures)+len(result.errors)
    passed=result.testsRun-pending-problems
    print(f"\n완료 {passed} / 미완성 {pending} / 확인 필요 {problems}")
    if pending: print("미완성은 TODO가 남아 있다는 뜻입니다. 완료된 것으로 표시하지 않습니다.")
    print("설명·이해 여부는 코드 실행 후 본인의 말로 확인합니다.")
    return 1 if problems else (2 if pending else 0)


if __name__=="__main__": raise SystemExit(main())
