"""Convenience launcher for the CHRONOS-SAFE web interface."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent / "chronos_safe"
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))

    from chronos_safe.runtime import run_web_server

    run_web_server()


if __name__ == "__main__":
    main()
