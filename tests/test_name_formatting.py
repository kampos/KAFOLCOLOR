from __future__ import annotations

import unittest

from folder_palette_common import humanize_filename


class TestNameFormatting(unittest.TestCase):
    def test_formats_dash_and_underscore_names(self) -> None:
        self.assertEqual(humanize_filename("proyecto-importante.svg"), "Proyecto importante")
        self.assertEqual(humanize_filename("clientes_2026.png"), "Clientes 2026")

    def test_handles_empty_stem(self) -> None:
        self.assertEqual(humanize_filename(".svg"), "Icono")


if __name__ == "__main__":
    unittest.main()
