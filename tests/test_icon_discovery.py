from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from folder_palette_common import discover_custom_icons


class TestIconDiscovery(unittest.TestCase):
    def test_discovers_supported_files_and_sorts_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "clientes_2026.png").write_text("x", encoding="utf-8")
            (root / "proyecto-importante.svg").write_text("x", encoding="utf-8")
            (root / ".oculto.svg").write_text("x", encoding="utf-8")
            (root / "no-soportado.txt").write_text("x", encoding="utf-8")
            (root / "subdir").mkdir()

            icons = discover_custom_icons(root)

            self.assertEqual([item.label for item in icons], ["Clientes 2026", "Proyecto importante"])
            self.assertTrue(all(item.path.exists() for item in icons))


if __name__ == "__main__":
    unittest.main()
