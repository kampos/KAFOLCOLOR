from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import gi

for _nautilus_version in ("4.1", "4.0"):
    try:
        gi.require_version("Nautilus", _nautilus_version)
        break
    except ValueError:
        continue
gi.require_version("GObject", "2.0")
from gi.repository import GObject, Nautilus


def _add_common_paths() -> None:
    this_file = Path(__file__).resolve()
    candidates = [
        Path("/usr/share/folder-palette"),
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "folder-palette" / "bin",
        this_file.parent.parent / "common",
        this_file.parents[2] / "common" if len(this_file.parents) > 2 else None,
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        module_file = candidate / "folder_palette_common.py"
        if module_file.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


_add_common_paths()

from folder_palette_common import (  # noqa: E402
    BIN_DIR,
    CUSTOM_ICONS_DIR,
    DEFAULT_ICON_FILES,
    apply_icon_to_multiple_folders,
    build_failure_message,
    discover_custom_icons,
    ensure_runtime_directories,
    get_logger,
    open_custom_icons_directory,
    resolve_default_icon_path,
    restore_icon_for_multiple_folders,
    validate_folder_paths,
)


class FolderPaletteExtension(GObject.GObject, Nautilus.MenuProvider):
    def _selected_paths(self, files) -> list[Path] | None:
        selected_paths: list[Path] = []
        for file_info in files:
            location = file_info.get_location()
            if location is None:
                return None
            path = location.get_path()
            if not path or not file_info.is_directory():
                return None
            selected_paths.append(Path(path))
        validation = validate_folder_paths(selected_paths)
        if not validation.ok:
            return None
        return list(validation.accepted)

    def _menu_item(self, name: str, label: str) -> Nautilus.MenuItem:
        return Nautilus.MenuItem(name=name, label=label)

    def _apply_icon(self, _menu_item, folder_paths, icon_path) -> None:
        result = apply_icon_to_multiple_folders(folder_paths, icon_path)
        if result.failed:
            get_logger().error("No se pudo aplicar el icono:\n%s", build_failure_message(result.failed))

    def _restore_icon(self, _menu_item, folder_paths) -> None:
        result = restore_icon_for_multiple_folders(folder_paths)
        if result.failed:
            get_logger().error("No se pudo restaurar el icono:\n%s", build_failure_message(result.failed))

    def _launch_gallery(self, _menu_item, folder_paths) -> None:
        gallery_candidates = [
            BIN_DIR / "folder-palette-gallery.py",
            Path("/usr/share/folder-palette/folder-palette-gallery.py"),
            Path(__file__).resolve().parents[1] / "gallery" / "folder-palette-gallery.py",
        ]
        gallery_script = next((candidate for candidate in gallery_candidates if candidate.exists()), None)
        if gallery_script is None:
            get_logger().error("No se encontró la galería folder-palette-gallery.py")
            return
        try:
            subprocess.Popen([sys.executable, str(gallery_script), *[str(path) for path in folder_paths]])
        except Exception as exc:
            get_logger().exception("No se pudo abrir la galería", exc_info=exc)

    def _open_custom_icons(self, _menu_item, _folder_paths) -> None:
        result = open_custom_icons_directory()
        if not result.success:
            get_logger().error(result.message)

    def _build_default_colors_menu(self, folder_paths) -> Nautilus.MenuItem:
        submenu_item = self._menu_item("folder-palette-default-colors", "Colores predeterminados")
        submenu = Nautilus.Menu()
        ensure_runtime_directories()
        for label, filename in DEFAULT_ICON_FILES:
            icon_path = resolve_default_icon_path(filename)
            item = self._menu_item(f"folder-palette-{filename}", label)
            item.connect("activate", self._apply_icon, folder_paths, icon_path)
            submenu.append_item(item)
        submenu_item.set_submenu(submenu)
        return submenu_item

    def _build_custom_icons_menu(self, folder_paths) -> Nautilus.MenuItem:
        submenu_item = self._menu_item("folder-palette-custom-icons", "Iconos personalizados")
        submenu = Nautilus.Menu()
        custom_icons = discover_custom_icons()
        if not custom_icons:
            empty_item = self._menu_item("folder-palette-no-custom-icons", "No hay iconos personalizados")
            empty_item.set_property("sensitive", False)
            submenu.append_item(empty_item)
        else:
            for index, icon_asset in enumerate(custom_icons):
                item = self._menu_item(f"folder-palette-custom-{index}", icon_asset.label)
                item.connect("activate", self._apply_icon, folder_paths, icon_asset.path)
                submenu.append_item(item)

        refresh_item = self._menu_item("folder-palette-refresh-custom-icons", "Actualizar lista")
        refresh_item.connect("activate", self._refresh_menu_only, folder_paths)
        submenu.append_item(refresh_item)
        submenu_item.set_submenu(submenu)
        return submenu_item

    def _refresh_menu_only(self, _menu_item, _folder_paths) -> None:
        # Nautilus reconstruye el menú cuando se vuelve a abrir.
        return

    def get_file_items(self, files):
        folder_paths = self._selected_paths(files)
        if not folder_paths:
            return None

        main_item = self._menu_item("folder-palette-main", "Cambiar color o icono")
        main_menu = Nautilus.Menu()

        main_menu.append_item(self._build_default_colors_menu(folder_paths))
        main_menu.append_item(self._build_custom_icons_menu(folder_paths))

        gallery_item = self._menu_item("folder-palette-open-gallery", "Abrir galería de iconos personalizados")
        gallery_item.connect("activate", self._launch_gallery, folder_paths)
        main_menu.append_item(gallery_item)

        open_folder_item = self._menu_item("folder-palette-open-folder", "Abrir carpeta de iconos personalizados")
        open_folder_item.connect("activate", self._open_custom_icons, folder_paths)
        main_menu.append_item(open_folder_item)

        restore_item = self._menu_item("folder-palette-restore", "Restaurar icono original")
        restore_item.connect("activate", self._restore_icon, folder_paths)
        main_menu.append_item(restore_item)

        main_item.set_submenu(main_menu)
        return [main_item]
