"""Inicializador da interface web do CHRONOS-SEGURO."""

from __future__ import annotations

from chronos_seguro.execucao import run_web_server


def main() -> None:
    run_web_server()


if __name__ == "__main__":
    main()
