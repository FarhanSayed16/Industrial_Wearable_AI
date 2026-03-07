#!/usr/bin/env python3
"""Run edge gateway. Use: python run.py (from project root) or python -m edge.run"""
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
os.chdir(_root)

if __name__ == "__main__":
    from edge.src.main import _run_edge
    _run_edge()
