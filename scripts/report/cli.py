from __future__ import annotations

import argparse
from pathlib import Path

from .run_analysis import analyze_run, write_run_analysis
from .session import generate_report
from .session_io import write_session_report


def main() -> int:
    parser = argparse.ArgumentParser(description="urisys session report generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Generate report for one session directory")
    gen.add_argument("session_dir", type=Path)

    ana = sub.add_parser("analyze", help="Analyze all sessions in a run directory")
    ana.add_argument("run_dir", type=Path)
    ana.add_argument("--write-md", action="store_true")

    args = parser.parse_args()

    if args.cmd == "generate":
        report = generate_report(args.session_dir)
        json_path, md_path = write_session_report(args.session_dir, report)
        print(f"report: {json_path}")
        print(f"markdown: {md_path}")
        print(f"status: {report.status.upper()} steps={report.passed}/{len(report.steps)}")
        return 0 if report.status == "pass" else 1

    analysis = analyze_run(args.run_dir)
    json_path, md_path = write_run_analysis(args.run_dir, analysis)
    print(f"analysis: {json_path}")
    print(f"markdown: {md_path}")
    print(
        f"SUMMARY pass={analysis.summary.get('pass', 0)} "
        f"fail={analysis.summary.get('fail', 0)} "
        f"error={analysis.summary.get('error', 0)}"
    )
    return 0 if analysis.all_passed else 1
