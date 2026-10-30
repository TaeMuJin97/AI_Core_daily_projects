# -*- coding: utf-8 -*-
"""Day2 제공 검사 도구. 학습자가 이 파일을 구현하거나 수정할 필요는 없다.

실행 예: python tools/check.py --exercise 07 --level advanced
문법 검사 후 별도 프로세스에서 CLI/함수 결과를 비교한다.
신뢰할 수 있는 자신의 실습 코드만 검사한다. 이 도구는 보안 샌드박스가 아니다.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import io
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LEVEL_MAP = {"basic": 1, "applied": 2, "advanced": 3}


def same_value(actual, expected):
    """수치 오차는 허용하되 bool과 정수 및 문자열 등 자료형을 구별한다."""
    if isinstance(expected, bool):
        return isinstance(actual, bool) and actual is expected
    if expected is None:
        return actual is None
    if isinstance(expected, (int, float)):
        return (isinstance(actual, (int, float)) and not isinstance(actual, bool)
                and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9))
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            same_value(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and set(actual) == set(expected) and all(
            same_value(actual[key], value) for key, value in expected.items())
    return type(actual) is type(expected) and actual == expected


def _function_worker(target):
    """제공된 함수 호출을 별도 프로세스에서 실행하는 내부 모드."""
    payload = json.load(sys.stdin)
    args = copy.deepcopy(payload.get("args", []))
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured):
            namespace = runpy.run_path(str(target), run_name="__day2_check__")
            result = namespace[payload["function"]](*args)
        # Tuple도 JSON 배열로 정규화하여 명시된 계약과 비교한다.
        response = {"ok": True, "return": result, "args": args, "stdout": captured.getvalue()}
    except Exception as exc:
        response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(response, ensure_ascii=False))


def run_case(case):
    target = (ROOT / case["path"]).resolve()
    if not target.is_relative_to(ROOT):
        return False, "허용된 실습 폴더 밖의 경로입니다."
    if not target.is_file():
        return False, f"파일 없음: {case['path']}"
    try:
        ast.parse(target.read_text(encoding="utf-8-sig"), filename=str(target))
    except (SyntaxError, UnicodeError) as exc:
        return False, f"문법/인코딩 오류: {exc}"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    function_mode = case["kind"] == "function"
    if function_mode:
        command = [sys.executable, "-S", "-X", "utf8", str(Path(__file__).resolve()), "--_probe", str(target)]
        supplied_input = json.dumps(case, ensure_ascii=False)
    else:
        # -S는 외부 site 패키지 없이도 핵심 실습이 실행되는지 확인한다.
        # 실제 패키지/venv를 조사하는 00 심화만 정상 site 초기화를 사용한다.
        options = [] if case["exercise"] == "00" and case["level"] == 3 else ["-S"]
        command = [sys.executable] + options + ["-X", "utf8", str(target)]
        supplied_input = case.get("stdin", "")
    try:
        # 실습 폴더가 아닌 임시 디렉터리에서 실행해 작업 디렉터리 의존성을 드러낸다.
        with tempfile.TemporaryDirectory(prefix="day2_check_") as working:
            proc = subprocess.run(command, input=supplied_input, text=True, encoding="utf-8",
                                  errors="replace", capture_output=True, cwd=working, env=env, timeout=8)
    except subprocess.TimeoutExpired:
        return False, "8초 시간 초과: while 종료 조건과 입력 소비 순서를 확인하세요."
    except OSError as exc:
        return False, f"실행기 오류: {exc}"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or f"종료 코드 {proc.returncode}")[-1100:]
    if function_mode:
        try:
            response = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return False, f"함수 결과를 해석할 수 없습니다: {proc.stdout[-500:]}"
        if not response.get("ok"):
            return False, response.get("error", "함수 실행 실패")
        if not same_value(response["return"], case.get("expected_return")):
            return False, f"반환값 기대={case.get('expected_return')!r}, 실제={response['return']!r}"
        for index, expected in case.get("expected_args", {}).items():
            actual = response["args"][int(index)]
            if not same_value(actual, expected):
                return False, f"인수 {index}의 실행 후 상태 기대={expected!r}, 실제={actual!r}"
        if response["stdout"] != case.get("expected_stdout", ""):
            return False, f"함수 출력 기대={case.get('expected_stdout', '')!r}, 실제={response['stdout']!r}"
        return True, "반환값·출력·상태 확인"
    actual = proc.stdout.replace("\r\n", "\n")
    if "expected_stdout" in case and actual != case["expected_stdout"]:
        expected = case["expected_stdout"]
        return False, f"출력 불일치\n  기대: {expected[:850]!r}\n  실제: {actual[:850]!r}"
    for part in case.get("contains", []):
        if part not in actual:
            return False, f"출력에 필요한 내용 없음: {part!r}"
    for part in case.get("not_contains", []):
        if part in actual:
            return False, f"출력에 남아 있는 금지/미완성 표시: {part!r}"
    return True, "실행 출력 확인"


def main():
    parser = argparse.ArgumentParser(description="Day2 실습 선택 검사 (제공 도구)")
    parser.add_argument("--exercise", choices=[f"{i:02d}" for i in range(8)])
    parser.add_argument("--level", choices=list(LEVEL_MAP))
    parser.add_argument("--all", action="store_true", help="24개 핵심 과제와 심화 직접 작성 테스트 검사")
    parser.add_argument("--list", action="store_true", help="검사 대상 목록")
    parser.add_argument("--report", help="선택: 검사 결과를 JSON으로 저장할 경로")
    args = parser.parse_args()
    spec_path = ROOT / "tools" / "cases.json"
    try:
        cases = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"검사 명세를 읽을 수 없습니다: {exc}")
    if args.list:
        for ex in [f"{i:02d}" for i in range(8)]:
            for level in [1, 2, 3]:
                selected = [c for c in cases if c["exercise"] == ex and c["level"] == level]
                if selected:
                    print(f"실습 {ex} / {['기본필수', '응용', '심화'][level - 1]}: {len(selected)}건")
        return 0
    if not args.all and args.exercise is None:
        parser.error("--exercise 01 --level basic 또는 --all을 지정하세요.")
    selected = cases
    if args.exercise:
        selected = [c for c in selected if c["exercise"] == args.exercise]
    if args.level:
        selected = [c for c in selected if c["level"] == LEVEL_MAP[args.level]]
    results = []
    for case in selected:
        passed, detail = run_case(case)
        results.append({"id": case["id"], "path": case["path"], "passed": passed, "detail": detail})
        print(f"{'PASS' if passed else 'FAIL'} {case['id']}")
        if not passed:
            print("  " + detail.replace("\n", "\n  "))
    passed_count = sum(item["passed"] for item in results)
    print(f"\n결과: {passed_count}/{len(results)} 통과")
    print("실습 00 환경의 실제 실행기·설치 버전과 설명·협업은 별도 확인합니다.")
    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {"python": sys.version, "passed": passed_count, "total": len(results), "results": results}
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"보고서: {report_path}")
    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--_probe":
        _function_worker(Path(sys.argv[2]))
    else:
        raise SystemExit(main())
