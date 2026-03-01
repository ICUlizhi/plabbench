#!/usr/bin/env python3
"""
PKU Minic 编译原理课程评测脚本

Usage:
    python runner.py --lab lab1-lexer
    python runner.py --lab lab2-parser --ai claude-code
    python runner.py --all
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


LAB_CONFIG = {
    "lab1-lexer": {
        "dir": "source",
        "build_cmd": ["make"],
        "test_cmd": ["make", "test"],
    },
    "lab2-parser": {
        "dir": "source",
        "build_cmd": ["make"],
        "test_cmd": ["make", "test"],
    },
    "lab3-semantics": {
        "dir": "source",
        "build_cmd": ["make"],
        "test_cmd": ["make", "test"],
    },
    "lab4-codegen": {
        "dir": "source",
        "build_cmd": ["make"],
        "test_cmd": ["make", "test"],
    },
    "lab5-optimize": {
        "dir": "source",
        "build_cmd": ["make"],
        "test_cmd": ["make", "test"],
    },
}


class BenchmarkRunner:
    def __init__(self, lab: str, ai: str, lab_dir: Path):
        self.lab = lab
        self.ai = ai
        self.lab_dir = lab_dir
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)

    def run(self) -> Dict:
        print(f"=" * 60)
        print(f"Running benchmark for {self.lab}")
        print(f"AI: {self.ai}")
        print(f"=" * 60)

        source_dir = self.lab_dir / self.lab / "source"
        if not source_dir.exists():
            print(f"Error: Source directory not found: {source_dir}")
            return self._create_error_result("Source not found")

        config = LAB_CONFIG.get(self.lab)
        if not config:
            return self._create_error_result(f"Unknown lab: {self.lab}")

        start_time = time.time()
        test_results = self._run_tests(source_dir, config)
        elapsed_time = time.time() - start_time

        result = {
            "lab": self.lab,
            "ai": self.ai,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_seconds": round(elapsed_time, 2),
            "results": {
                "total_tests": test_results["total"],
                "passed": test_results["passed"],
                "failed": test_results["failed"],
                "pass_rate": round(test_results["passed"] / max(test_results["total"], 1), 3),
            },
            "details": test_results.get("details", []),
        }

        self._save_result(result)
        self._print_summary(result)
        return result

    def _run_tests(self, source_dir: Path, config: Dict) -> Dict:
        print("\n[1/2] Building project...")
        build_result = self._build_project(source_dir, config)
        if not build_result:
            return {"total": 0, "passed": 0, "failed": 0, "details": []}

        print("\n[2/2] Running tests...")
        return self._run_test_suite(source_dir, config)

    def _build_project(self, source_dir: Path, config: Dict) -> bool:
        try:
            os.chdir(source_dir)
            result = subprocess.run(
                config["build_cmd"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                print(f"Build failed:\n{result.stderr}")
                return False
            print("Build successful")
            return True
        except Exception as e:
            print(f"Build error: {e}")
            return False

    def _run_test_suite(self, source_dir: Path, config: Dict) -> Dict:
        details = []
        passed = 0
        failed = 0

        try:
            os.chdir(source_dir)
            result = subprocess.run(
                config["test_cmd"],
                capture_output=True,
                text=True,
                timeout=300
            )

            # 解析测试结果
            for line in result.stdout.split("\n"):
                if "PASS" in line or "FAIL" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        test_name = parts[0]
                        status = "PASS" if "PASS" in line else "FAIL"
                        if status == "PASS":
                            passed += 1
                        else:
                            failed += 1
                        details.append({"test": test_name, "status": status})

        except Exception as e:
            print(f"Test error: {e}")

        total = passed + failed
        return {"total": total, "passed": passed, "failed": failed, "details": details}

    def _create_error_result(self, error_msg: str) -> Dict:
        return {
            "lab": self.lab,
            "ai": self.ai,
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "results": {"total_tests": 0, "passed": 0, "failed": 0, "pass_rate": 0},
        }

    def _save_result(self, result: Dict):
        filename = f"{self.lab}_{self.ai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        filepath.write_text(json.dumps(result, indent=2))
        print(f"\nResults saved to: {filepath}")

        latest_path = self.results_dir / "latest.json"
        latest_path.write_text(json.dumps(result, indent=2))

    def _print_summary(self, result: Dict):
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        if "error" in result:
            print(f"Error: {result['error']}")
            return

        r = result["results"]
        print(f"Total Tests: {r['total_tests']}")
        print(f"Passed: {r['passed']}")
        print(f"Failed: {r['failed']}")
        print(f"Pass Rate: {r['pass_rate']:.1%}")
        print(f"Elapsed Time: {result['elapsed_time_seconds']:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="PKU Minic Benchmark Runner")
    parser.add_argument("--lab", choices=list(LAB_CONFIG.keys()), help="Lab to benchmark")
    parser.add_argument("--ai", default="unknown", help="AI assistant name")
    parser.add_argument("--lab-dir", type=Path,
                        default=Path(__file__).parent.parent / "labs",
                        help="Directory containing lab source code")
    parser.add_argument("--all", action="store_true", help="Run all labs")

    args = parser.parse_args()

    if args.all:
        for lab in LAB_CONFIG.keys():
            runner = BenchmarkRunner(lab, args.ai, args.lab_dir)
            runner.run()
            print("\n")
    elif args.lab:
        runner = BenchmarkRunner(args.lab, args.ai, args.lab_dir)
        runner.run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
