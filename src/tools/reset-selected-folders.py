from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _add_common_paths() -> None:
    this_file = Path(__file__).resolve()
    candidates = [
        Path("/usr/share/folder-palette"),
        this_file.parent.parent / "common",
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "folder-palette" / "bin",
    ]
    for candidate in candidates:
        module_file = candidate / "folder_palette_common.py"
        if module_file.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


_add_common_paths()

from folder_palette_common import build_failure_message, restore_icon_for_multiple_folders  # noqa: E402


def parse_args(argv: list[str]) -> list[Path]:
    parser = argparse.ArgumentParser(
        description="Elimina metadata::custom-icon de carpetas indicadas manualmente."
    )
    parser.add_argument("folders", nargs="+", help="Rutas de carpetas a restaurar")
    parsed = parser.parse_args(argv)
    return [Path(item).expanduser() for item in parsed.folders]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        folders = parse_args(args)
    except SystemExit:
        return 1

    result = restore_icon_for_multiple_folders(folders)
    if result.failed:
        print("No se pudieron restaurar algunas carpetas:")
        print(build_failure_message(result.failed))
    if result.succeeded:
        print(f"Restauradas {len(result.succeeded)} carpetas.")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
