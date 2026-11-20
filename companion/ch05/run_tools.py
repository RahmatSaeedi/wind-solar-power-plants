"""Runs the chapter 5 command-line programs exactly as a reader would and saves
what they print (with the command line) into companion/ch05/expected/t_*.txt.

    python -m companion.ch05.run_tools
"""
from __future__ import annotations

import subprocess
import sys

from companion.ch05.common import HERE, emit

ROOT = HERE.parents[1]


def session(name: str, commands: list[str]) -> None:
    lines = []
    for cmd in commands:
        lines.append(f"$ python -m {cmd}")
        p = subprocess.run([sys.executable, "-m"] + cmd.split(), cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8")
        out = (p.stdout + p.stderr).rstrip("\n")
        lines += out.splitlines() if out else []
        lines.append(f"[exit code {p.returncode}]")
    emit(name, lines)


if __name__ == "__main__":
    c = "companion.ch05."
    session("t_step1", [c + "step1_convert 46.8 km/h m/s", c + "step1_convert 25 degC K",
                        c + "step1_convert -300 degC K", c + "step1_convert 5 MW MWh",
                        c + "step1_convert 1 furlong m"])
    session("t_step2", [c + "step2_reader"])
    session("t_step4", [c + "step4_run companion/ch05/config/run_S0.yml",
                        c + "step4_run companion/ch05/config/run_bad.yml"])
    session("t_tool", [c + "resource_tool --version",
                       c + "resource_tool validate-raw",
                       c + "resource_tool run companion/ch05/config/run_S0.yml",
                       c + "resource_tool run companion/ch05/config/run_S1.yml",
                       c + "resource_tool report companion/ch05/output/S0"])
    session("t_help", [c + "resource_tool --help"])
    session("t_stage1", [c + "project_stage1"])
    session("t_check", [c + "check_all"])
    report = (HERE / "output" / "S0" / "PLP-GEN-REP-0002_rev-A.md").read_text("utf-8")
    emit("t_report", report.rstrip("\n").splitlines())
