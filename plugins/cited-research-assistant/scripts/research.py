#!/usr/bin/env python3
"""Run the research helper that lives in the skill folder.

That folder is the only copy, so it still runs when copied on its own.
Plugin commands keep calling this path.
"""
import os
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / 'skills' / 'cited-research-assistant' / 'scripts' / 'research.py'

if __name__ == '__main__':
    if not TARGET.is_file():
        sys.stderr.write('error: skill research helper not found\n')
        raise SystemExit(1)
    os.execv(sys.executable, [sys.executable, str(TARGET), *sys.argv[1:]])
