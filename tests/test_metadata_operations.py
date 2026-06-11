from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import folder_palette_common as common


class TestMetadataOperations(unittest.TestCase):
    def test_apply_icon_uses_gio_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "folder"
            folder.mkdir()
            icon = root / "icon.svg"
            icon.write_text("<svg/>", encoding="utf-8")

            with patch.object(common, "_gio_set_custom_icon") as gio_set, patch.object(
                common, "_subprocess_set_custom_icon"
            ) as subprocess_set, patch.object(common, "_notify_nautilus_folder_changed") as notify:
                gio_set.return_value = None
                result = common.apply_icon_to_folder(folder, icon)

            self.assertTrue(result.success)
            gio_set.assert_called_once()
            subprocess_set.assert_not_called()
            notify.assert_called_once_with(folder.resolve())

    def test_restore_icon_uses_gio_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "folder"
            folder.mkdir()

            with patch.object(common, "_gio_unset_custom_icon") as gio_unset, patch.object(
                common, "_subprocess_unset_custom_icon"
            ) as subprocess_unset, patch.object(common, "_notify_nautilus_folder_changed") as notify:
                gio_unset.return_value = None
                result = common.restore_icon_for_folder(folder)

            self.assertTrue(result.success)
            gio_unset.assert_called_once()
            subprocess_unset.assert_not_called()
            notify.assert_called_once_with(folder.resolve())

    def test_notify_failure_does_not_fail_successful_icon_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "folder"
            folder.mkdir()
            icon = root / "icon.svg"
            icon.write_text("<svg/>", encoding="utf-8")

            with patch.object(common, "_gio_set_custom_icon") as gio_set, patch.object(
                common, "_notify_nautilus_folder_changed", side_effect=OSError("sin permisos")
            ):
                gio_set.return_value = None
                result = common.apply_icon_to_folder(folder, icon)

            self.assertTrue(result.success)

    def test_batch_application_collects_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder_a = root / "a"
            folder_b = root / "b"
            folder_a.mkdir()
            folder_b.mkdir()
            icon = root / "icon.svg"
            icon.write_text("<svg/>", encoding="utf-8")

            def fake_apply(folder_path: Path, icon_path: Path) -> common.OperationResult:
                if folder_path == folder_a:
                    return common.OperationResult(folder_path, True, "ok", icon_path.resolve().as_uri())
                return common.OperationResult(folder_path, False, "falló", None)

            with patch.object(common, "apply_icon_to_folder", side_effect=fake_apply):
                result = common.apply_icon_to_multiple_folders([folder_a, folder_b], icon)

            self.assertEqual(len(result.succeeded), 1)
            self.assertEqual(len(result.failed), 1)


if __name__ == "__main__":
    unittest.main()
