from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from folder_palette_common import validate_folder_paths


class TestPathValidation(unittest.TestCase):
    def test_accepts_only_local_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "carpeta"
            folder.mkdir()
            file_path = root / "archivo.txt"
            file_path.write_text("x", encoding="utf-8")

            result = validate_folder_paths([folder, file_path, root / "inexistente"])

            self.assertEqual(result.accepted, (folder.resolve(),))
            self.assertEqual(len(result.rejected), 2)


if __name__ == "__main__":
    unittest.main()

