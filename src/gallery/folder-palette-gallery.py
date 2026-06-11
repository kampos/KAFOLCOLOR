from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gio, Gtk


def _add_common_paths() -> None:
    this_file = Path(__file__).resolve()
    candidates = [
        this_file.parent,
        Path("/usr/share/folder-palette"),
        this_file.parent.parent / "common",
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "folder-palette" / "bin",
    ]
    for candidate in candidates:
        module_file = candidate / "folder_palette_common.py"
        if module_file.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


_add_common_paths()

from folder_palette_common import (  # noqa: E402
    CUSTOM_ICONS_DIR,
    IconAsset,
    apply_icon_to_multiple_folders,
    build_failure_message,
    discover_custom_icons,
    ensure_runtime_directories,
    get_default_icon_assets,
    get_logger,
    humanize_filename,
    open_custom_icons_directory,
    restore_icon_for_multiple_folders,
    validate_folder_paths,
)


class GalleryWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application, raw_folder_paths: list[Path]) -> None:
        super().__init__(application=app)
        self.raw_folder_paths = raw_folder_paths
        self.folder_paths: list[Path] = []
        self._cards: list[Gtk.Widget] = []

        self.set_default_size(860, 640)
        self.set_title(self._build_title(len(raw_folder_paths)))

        ensure_runtime_directories()

        validation = validate_folder_paths(raw_folder_paths)
        self.folder_paths = list(validation.accepted)
        self._validation_rejected = list(validation.rejected)

        self._build_ui()

        if self._validation_rejected:
            rejection_lines = "\n".join(
                f"- {path}: {reason}" for path, reason in self._validation_rejected
            )
            self._show_error(
                "No se pudieron usar algunas rutas",
                rejection_lines,
            )
        if not self.folder_paths:
            self._show_error(
                "No hay carpetas válidas",
                "La galería necesita al menos una carpeta local válida para aplicar iconos.",
            )
            self.close()

    def _build_title(self, count: int) -> str:
        if count == 1:
            return "Seleccionar icono para la carpeta"
        return "Seleccionar icono para las carpetas seleccionadas"

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        root.set_margin_top(20)
        root.set_margin_bottom(20)
        root.set_margin_start(20)
        root.set_margin_end(20)

        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        title = Gtk.Label(label=self._build_title(len(self.raw_folder_paths)))
        title.add_css_class("title-1")
        title.set_wrap(True)
        title.set_xalign(0.0)
        subtitle = Gtk.Label(label="Elige un color, icono personalizado o restaura el icono original.")
        subtitle.add_css_class("dim-label")
        subtitle.set_wrap(True)
        subtitle.set_xalign(0.0)
        header.append(title)
        header.append(subtitle)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions.set_hexpand(True)
        refresh_button = Gtk.Button(label="Actualizar")
        refresh_button.connect("clicked", self._on_refresh)
        open_folder_button = Gtk.Button(label="Abrir carpeta de iconos")
        open_folder_button.connect("clicked", self._on_open_folder)
        actions.append(refresh_button)
        actions.append(open_folder_button)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_column_spacing(12)
        self.flowbox.set_row_spacing(12)
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_homogeneous(True)

        scroller = Gtk.ScrolledWindow()
        scroller.set_hexpand(True)
        scroller.set_vexpand(True)
        scroller.set_child(self.flowbox)

        root.append(header)
        root.append(actions)
        root.append(scroller)
        self.set_child(root)
        self._rebuild_cards()

    def _show_error(self, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
            secondary_text=message,
        )
        dialog.connect("response", lambda dlg, _response: dlg.destroy())
        dialog.present()

    def _clear_cards(self) -> None:
        while True:
            child = self.flowbox.get_first_child()
            if child is None:
                break
            self.flowbox.remove(child)
        self._cards.clear()

    def _rebuild_cards(self) -> None:
        self._clear_cards()

        for icon_asset in get_default_icon_assets():
            self._cards.append(self._create_icon_card(icon_asset))

        for icon_asset in discover_custom_icons():
            self._cards.append(self._create_icon_card(icon_asset))

        self._cards.append(self._create_restore_card())

        for card in self._cards:
            self.flowbox.append(card)

    def _icon_preview(self, icon_asset: IconAsset) -> Gtk.Widget:
        picture = Gtk.Picture.new_for_file(Gio.File.new_for_path(str(icon_asset.path)))
        picture.set_can_shrink(True)
        picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        picture.set_size_request(96, 96)
        return picture

    def _make_card(self, title: str, preview: Gtk.Widget, subtitle: str, on_click) -> Gtk.Widget:
        button = Gtk.Button()
        button.add_css_class("card")
        button.set_hexpand(True)
        button.set_vexpand(False)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        inner.set_margin_top(12)
        inner.set_margin_bottom(12)
        inner.set_margin_start(12)
        inner.set_margin_end(12)
        inner.set_halign(Gtk.Align.CENTER)

        inner.append(preview)

        label = Gtk.Label(label=title)
        label.set_wrap(True)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_xalign(0.5)
        label.add_css_class("heading")

        detail = Gtk.Label(label=subtitle)
        detail.set_wrap(True)
        detail.set_justify(Gtk.Justification.CENTER)
        detail.set_xalign(0.5)
        detail.add_css_class("dim-label")

        inner.append(label)
        inner.append(detail)
        button.set_child(inner)
        button.connect("clicked", on_click)
        return button

    def _create_icon_card(self, icon_asset: IconAsset) -> Gtk.Widget:
        preview = self._icon_preview(icon_asset)
        subtitle = "Icono personalizado" if icon_asset.is_custom else "Color predeterminado"
        return self._make_card(icon_asset.label, preview, subtitle, lambda _button: self._apply_asset(icon_asset))

    def _create_restore_card(self) -> Gtk.Widget:
        preview = Gtk.Image.new_from_icon_name("edit-undo-symbolic")
        preview.set_pixel_size(64)
        return self._make_card(
            "Restaurar icono original",
            preview,
            "Eliminar metadata::custom-icon",
            lambda _button: self._restore_selected(),
        )

    def _apply_asset(self, icon_asset: IconAsset) -> None:
        if not self.folder_paths:
            return
        result = apply_icon_to_multiple_folders(self.folder_paths, icon_asset.path)
        if result.failed:
            self._show_error(
                "No se pudo aplicar el icono",
                build_failure_message(result.failed),
            )
        if result.ok:
            self.close()

    def _restore_selected(self) -> None:
        if not self.folder_paths:
            return
        result = restore_icon_for_multiple_folders(self.folder_paths)
        if result.failed:
            self._show_error(
                "No se pudo restaurar el icono original",
                build_failure_message(result.failed),
            )
        if result.ok:
            self.close()

    def _on_refresh(self, _button: Gtk.Button) -> None:
        self._rebuild_cards()

    def _on_open_folder(self, _button: Gtk.Button) -> None:
        result = open_custom_icons_directory()
        if not result.success:
            self._show_error("No se pudo abrir la carpeta de iconos", result.message)


class GalleryApplication(Gtk.Application):
    def __init__(self, folder_paths: list[Path]) -> None:
        super().__init__(application_id="com.folderpalette.gallery", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.folder_paths = folder_paths
        self.window: GalleryWindow | None = None

    def do_activate(self) -> None:
        if self.window is None:
            self.window = GalleryWindow(self, self.folder_paths)
        self.window.present()


def _parse_args(argv: list[str]) -> list[Path]:
    parser = argparse.ArgumentParser(description="Galería de iconos para Folder Palette")
    parser.add_argument("folders", nargs="+", help="Rutas de carpetas seleccionadas")
    parsed = parser.parse_args(argv)
    return [Path(item).expanduser() for item in parsed.folders]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        folder_paths = _parse_args(args)
    except SystemExit:
        return 1

    app = GalleryApplication(folder_paths)
    get_logger()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
