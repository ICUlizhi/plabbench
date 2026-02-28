#!/usr/bin/env python3
"""
PKU OS Lab 评测脚本

用于自动化评测 AI 助手在 PKU OS Lab 上的表现。

Usage:
    python runner.py --lab lab1-threads --track pintos
    python runner.py --lab lab1-threads --track pintos --ai claude-code
    python runner.py --all --track pintos
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


# Lab 配置
LAB_CONFIG = {
    "lab0-booting": {
        "pintos": {"dir": "threads", "test_cmd": "make check"},
        "tacos": {"dir": "kernel", "test_cmd": "cargo test"},
    },
    "lab1-threads": {
        "pintos": {"dir": "threads", "test_cmd": "make check"},
        "tacos": {"dir": "kernel", "test_cmd": "cargo test"},
    },
    "lab2-userprog": {
        "pintos": {"dir": "userprog", "test_cmd": "make check"},
        "tacos": {"dir": "kernel", "test_cmd": "cargo test"},
    },
    "lab3a-vm": {
        "pintos": {"dir": "vm", "test_cmd": "make check"},
        "tacos": {"dir": "kernel", "test_cmd": "cargo test"},
    },
    "lab3b-mmap": {
        "pintos": {"dir": "vm", "test_cmd": "make check"},
        # Tacos 无此 lab
    },
}

# 测试用例列表（Pintos）
PINTOS_TESTS = {
    "lab1-threads": [
        "alarm-single", "alarm-multiple", "alarm-simultaneous",
        "alarm-zero", "alarm-negative",
        "priority-change", "priority-preempt", "priority-fifo",
        "priority-donate-one", "priority-donate-multiple",
        "priority-donate-nest", "priority-donate-sema",
        "mlfqs-load-1", "mlfqs-load-60", "mlfqs-fair-2",
    ],
    "lab2-userprog": [
        "args-single", "args-multiple", "args-many",
        "sc-bad-sp", "sc-bad-arg", "sc-boundary",
        "exit", "halt",
        "create", "open", "close", "read", "write",
        "exec", "wait",
        "bad-read", "bad-write", "bad-jump",
    ],
    "lab3a-vm": [
        "page-linear", "page-parallel",
        "page-merge-seq", "page-merge-par",
        "page-merge-stk", "page-merge-mm",
        "page-shuffle",
        "mmap-read", "mmap-write",
        "bad-read", "bad-write",
    ],
    "lab3b-mmap": [
        "mmap-read", "mmap-write", "mmap-shuffle",
        "mmap-twice", "mmap-exit", "mmap-offest",
    ],
}


class BenchmarkRunner:
    """评测运行器"""

    def __init__(self, lab: str, track: str, ai: str, lab_dir: Path):
        self.lab = lab
        self.track = track
        self.ai = ai
        self.lab_dir = lab_dir
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)

    def run(self) -> Dict:
        """运行评测"""
        print(f"=" * 60)
        print(f"Running benchmark for {self.lab} ({self.track})")
        print(f"AI: {self.ai}")
        print(f"=" * 60)

        # 检查 lab 目录
        source_dir = self.lab_dir / self.track / "source"
        if not source_dir.exists():
            print(f"Error: Source directory not found: {source_dir}")
            print("Please clone the lab repository first.")
            return self._create_error_result("Source not found")

        # 获取配置
        config = LAB_CONFIG.get(self.lab, {}).get(self.track)
        if not config:
            return self._create_error_result(f"Unknown lab/track: {self.lab}/{self.track}")

        # 运行测试
        start_time = time.time()
        test_results = self._run_tests(source_dir, config)
        elapsed_time = time.time() - start_time

        # 生成结果
        result = {
            "lab": self.lab,
            "track": self.track,
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

        # 保存结果
        self._save_result(result)

        # 打印摘要
        self._print_summary(result)

        return result

    def _run_tests(self, source_dir: Path, config: Dict) -> Dict:
        """运行测试套件"""
        build_dir = source_dir / "src" / config["dir"] / "build"

        # 构建项目
        print("\n[1/2] Building project...")
        build_result = self._build_project(source_dir, config)
        if not build_result:
            return {"total": 0, "passed": 0, "failed": 0, "details": []}

        # 运行测试
        print("\n[2/2] Running tests...")
        return self._run_test_suite(build_dir, config)

    def _build_project(self, source_dir: Path, config: Dict) -> bool:
        """构建项目"""
        try:
            if self.track == "pintos":
                build_dir = source_dir / "src" / config["dir"]
                os.chdir(build_dir)
                result = subprocess.run(
                    ["make", "clean"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result = subprocess.run(
                    ["make"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode != 0:
                    print(f"Build failed:\n{result.stderr}")
                    return False
                print("Build successful")
                return True

            elif self.track == "tacos":
                os.chdir(source_dir / config["dir"])
                result = subprocess.run(
                    ["cargo", "build"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode != 0:
                    print(f"Build failed:\n{result.stderr}")
                    return False
                print("Build successful")
                return True

        except subprocess.TimeoutExpired:
            print("Build timeout")
            return False
        except Exception as e:
            print(f"Build error: {e}")
            return False

        return False

    def _run_test_suite(self, build_dir: Path, config: Dict) -> Dict:
        """运行测试套件并解析结果"""
        details = []
        passed = 0
        failed = 0

        try:
            if self.track == "pintos":
                # 运行 make check
                os.chdir(build_dir)
                result = subprocess.run(
                    ["make", "check"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                # 解析结果文件
                results_dir = build_dir / "tests" / config["dir"]
                if not results_dir.exists():
                    results_dir = build_dir / "tests"

                for result_file in results_dir.glob("*.result"):
                    test_name = result_file.stem
                    result_content = result_file.read_text().strip()
                    is_pass = "PASS" in result_content

                    if is_pass:
                        passed += 1
                        status = "PASS"
                    else:
                        failed += 1
                        status = "FAIL"

                    details.append({
                        "test": test_name,
                        "status": status,
                    })

            elif self.track == "tacos":
                os.chdir(build_dir.parent)  # kernel directory
                result = subprocess.run(
                    ["cargo", "test", "--", "--nocapture"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                # 解析 cargo test 输出
                for line in result.stdout.split("\n"):
                    if "test" in line and "..." in line:
                        parts = line.split("...")
                        if len(parts) == 2:
                            test_name = parts[0].replace("test", "").strip()
                            status_str = parts[1].strip()
                            is_pass = "ok" in status_str

                            if is_pass:
                                passed += 1
                                status = "PASS"
                            else:
                                failed += 1
                                status = "FAIL"

                            details.append({
                                "test": test_name,
                                "status": status,
                            })

        except subprocess.TimeoutExpired:
            print("Test timeout")
        except Exception as e:
            print(f"Test error: {e}")

        total = passed + failed
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "details": details,
        }

    def _create_error_result(self, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            "lab": self.lab,
            "track": self.track,
            "ai": self.ai,
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "results": {"total_tests": 0, "passed": 0, "failed": 0, "pass_rate": 0},
        }

    def _save_result(self, result: Dict):
        """保存结果到文件"""
        filename = f"{self.lab}_{self.track}_{self.ai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        filepath.write_text(json.dumps(result, indent=2))
        print(f"\nResults saved to: {filepath}")

        # 同时保存为 latest.json
        latest_path = self.results_dir / "latest.json"
        latest_path.write_text(json.dumps(result, indent=2))

    def _print_summary(self, result: Dict):
        """打印结果摘要"""
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

        if r["failed"] > 0 and result.get("details"):
            print("\nFailed Tests:")
            for detail in result["details"]:
                if detail["status"] == "FAIL":
                    print(f"  - {detail['test']}")


def main():
    parser = argparse.ArgumentParser(description="PKU OS Lab Benchmark Runner")
    parser.add_argument("--lab", choices=list(LAB_CONFIG.keys()),
                        help="Lab to benchmark")
    parser.add_argument("--track", choices=["pintos", "tacos"],
                        help="Track to use")
    parser.add_argument("--ai", default="unknown",
                        help="AI assistant name (claude-code, kimi-code, etc.)")
    parser.add_argument("--lab-dir", type=Path,
                        default=Path(__file__).parent.parent / "labs",
                        help="Directory containing lab source code")
    parser.add_argument("--all", action="store_true",
                        help="Run all labs for specified track")

    args = parser.parse_args()

    if args.all:
        # 运行所有 lab
        for lab in LAB_CONFIG.keys():
            if args.track in LAB_CONFIG[lab]:
                runner = BenchmarkRunner(lab, args.track, args.ai, args.lab_dir)
                runner.run()
                print("\n")
    elif args.lab and args.track:
        # 运行单个 lab
        runner = BenchmarkRunner(args.lab, args.track, args.ai, args.lab_dir)
        runner.run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
