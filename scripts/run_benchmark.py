#!/usr/bin/env python3
"""
批量评测脚本 - 运行所有 lab 的评测

Usage:
    python run_benchmark.py --ai claude-code --track pintos
    python run_benchmark.py --ai kimi-code --track tacos --lab lab1
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


LABS = ["lab0-booting", "lab1-threads", "lab2-userprog", "lab3a-vm", "lab3b-mmap"]


def run_benchmark(lab: str, track: str, ai: str) -> dict:
    """运行单个 lab 的评测"""
    runner_path = Path(__file__).parent.parent / "courses" / "pku-os" / "benchmark" / "runner.py"

    cmd = [
        sys.executable,
        str(runner_path),
        "--lab", lab,
        "--track", track,
        "--ai", ai,
    ]

    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # 读取结果
    results_dir = runner_path.parent / "results"
    latest_file = results_dir / "latest.json"

    if latest_file.exists():
        return json.loads(latest_file.read_text())
    else:
        return {"lab": lab, "track": track, "ai": ai, "error": "No results generated"}


def generate_report(results: list, ai: str, track: str) -> str:
    """生成评测报告"""
    lines = []
    lines.append("# Plabbench 评测报告")
    lines.append("")
    lines.append(f"- **AI**: {ai}")
    lines.append(f"- **Track**: {track}")
    lines.append(f"- **时间**: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## 结果汇总")
    lines.append("")
    lines.append("| Lab | 通过 | 失败 | 通过率 | 耗时 |")
    lines.append("|-----|------|------|--------|------|")

    for r in results:
        if "error" in r:
            lines.append(f"| {r['lab']} | - | - | 错误 | - |")
        else:
            res = r["results"]
            lines.append(
                f"| {r['lab']} | {res['passed']} | {res['failed']} | "
                f"{res['pass_rate']:.1%} | {r.get('elapsed_time_seconds', 0):.1f}s |"
            )

    lines.append("")
    lines.append("## 详细结果")
    lines.append("")

    for r in results:
        lines.append(f"### {r['lab']}")
        lines.append("")
        if "error" in r:
            lines.append(f"错误: {r['error']}")
        else:
            lines.append(f"- 通过: {r['results']['passed']}")
            lines.append(f"- 失败: {r['results']['failed']}")
            lines.append(f"- 通过率: {r['results']['pass_rate']:.1%}")

            if r.get('details'):
                failed_tests = [d for d in r['details'] if d['status'] == 'FAIL']
                if failed_tests:
                    lines.append("")
                    lines.append("失败的测试:")
                    for t in failed_tests:
                        lines.append(f"- {t['test']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run batch benchmark")
    parser.add_argument("--ai", required=True, help="AI assistant name")
    parser.add_argument("--track", required=True, choices=["pintos", "tacos"], help="Track to use")
    parser.add_argument("--lab", help="Run specific lab only")
    parser.add_argument("--output", type=Path, help="Output report file")

    args = parser.parse_args()

    # 确定要运行的 labs
    labs = [args.lab] if args.lab else LABS

    # 过滤掉 Tacos 没有的 lab3b
    if args.track == "tacos":
        labs = [l for l in labs if l != "lab3b-mmap"]

    # 运行评测
    results = []
    for lab in labs:
        result = run_benchmark(lab, args.track, args.ai)
        results.append(result)

    # 生成报告
    report = generate_report(results, args.ai, args.track)

    # 保存报告
    if args.output:
        args.output.write_text(report)
        print(f"\nReport saved to: {args.output}")
    else:
        output_path = Path(__file__).parent.parent / "docs" / "benchmarks" / f"{args.ai}_{args.track}_{datetime.now().strftime('%Y%m%d')}.md"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(report)
        print(f"\nReport saved to: {output_path}")

    print("\n" + "=" * 60)
    print("BATCH BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
