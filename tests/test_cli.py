"""별도 REPL 프로세스에서 기존 명령 흐름을 확인한다."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.smoke


def test_redis_repl_commands():
    commands = (
        "SET name redis\nGET name\nEXPIRE name 60\nTTL name\nDEL name\nGET name\nQUIT\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "mini_redis"],
        input=commands,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert '"redis"' in result.stdout and "(nil)" in result.stdout
    assert "(integer) 1" in result.stdout and "(error)" not in result.stdout
