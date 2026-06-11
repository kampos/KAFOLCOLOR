from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, Iterable, Sequence

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib


DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")).expanduser()
STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")).expanduser()

APP_DATA_DIR = DATA_HOME / "folder-palette"
SYSTEM_APP_DATA_DIR = Path("/usr/share/folder-palette")
DEFAULT_ICONS_DIR = APP_DATA_DIR / "icons" / "default"
SYSTEM_DEFAULT_ICONS_DIR = SYSTEM_APP_DATA_DIR / "icons" / "default"
CUSTOM_ICONS_DIR = APP_DATA_DIR / "custom-icons"
BIN_DIR = APP_DATA_DIR / "bin"
LOG_DIR = STATE_HOME / "folder-palette"
NAUTILUS_EXTENSION_DIR = DATA_HOME / "nautilus-python" / "extensions"

ALLOWED_ICON_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}

DEFAULT_ICON_FILES = (
    ("Rojo", "folder-red.svg"),
    ("Verde", "folder-green.svg"),
    ("Azul", "folder-blue.svg"),
    ("Amarillo", "folder-yellow.svg"),
    ("Negro", "folder-black.svg"),
    ("Blanco", "folder-white.svg"),
)


@dataclass(frozen=True)
class IconAsset:
    label: str
    path: Path
    is_custom: bool = False


@dataclass(frozen=True)
class OperationResult:
    path: Path
    success: bool
    message: str
    icon_uri: str | None = None


@dataclass(frozen=True)
class BatchResult:
    succeeded: tuple[OperationResult, ...]
    failed: tuple[OperationResult, ...]

    @property
    def ok(self) -> bool:
        return not self.failed


@dataclass(frozen=True)
class FolderValidationResult:
    accepted: tuple[Path, ...]
    rejected: tuple[tuple[Path, str], ...]

    @property
    def ok(self) -> bool:
        return not self.rejected and bool(self.accepted)


_LOGGER: logging.Logger | None = None


def ensure_runtime_directories() -> None:
    for directory in (APP_DATA_DIR, DEFAULT_ICONS_DIR, CUSTOM_ICONS_DIR, BIN_DIR, LOG_DIR):
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    ensure_runtime_directories()

    logger = logging.getLogger("folder-palette")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        try:
            handler = RotatingFileHandler(
                LOG_DIR / "folder-palette.log",
                maxBytes=512_000,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
            )
        except OSError:
            handler = logging.NullHandler()
        logger.addHandler(handler)

    _LOGGER = logger
    return logger


def log_error(message: str, exc: BaseException | None = None) -> None:
    logger = get_logger()
    if exc is None:
        logger.error(message)
    else:
        logger.exception(message, exc_info=exc)


def humanize_filename(filename: str | Path) -> str:
    path = Path(filename)
    if path.name.startswith(".") and path.stem == path.name:
        return "Icono"
    stem = path.stem if isinstance(filename, (str, Path)) else str(filename)
    normalized = re.sub(r"[_-]+", " ", stem)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return "Icono"
    return normalized.lower().capitalize()


def is_supported_icon_file(path: Path | str) -> bool:
    candidate = Path(path)
    return candidate.is_file() and candidate.suffix.lower() in ALLOWED_ICON_EXTENSIONS


def _resolve_candidate(path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    try:
        return candidate.resolve()
    except FileNotFoundError:
        return candidate.absolute()


def validate_folder_paths(folder_paths: Sequence[Path | str]) -> FolderValidationResult:
    accepted: list[Path] = []
    rejected: list[tuple[Path, str]] = []

    for raw_path in folder_paths:
        candidate = _resolve_candidate(raw_path)
        if not candidate.exists():
            rejected.append((candidate, "La carpeta no existe."))
            continue
        if not candidate.is_dir():
            rejected.append((candidate, "No es una carpeta."))
            continue
        if not Gio.File.new_for_path(str(candidate)).is_native():
            rejected.append((candidate, "La carpeta no es local."))
            continue
        accepted.append(candidate)

    return FolderValidationResult(tuple(accepted), tuple(rejected))


def resolve_default_icon_path(filename: str, base_dir: Path = DEFAULT_ICONS_DIR) -> Path:
    user_icon = (base_dir / filename).resolve()
    if user_icon.is_file():
        return user_icon
    return (SYSTEM_DEFAULT_ICONS_DIR / filename).resolve()


def get_default_icon_assets(base_dir: Path = DEFAULT_ICONS_DIR) -> list[IconAsset]:
    ensure_runtime_directories()
    assets: list[IconAsset] = []
    for label, filename in DEFAULT_ICON_FILES:
        icon_path = resolve_default_icon_path(filename, base_dir)
        if icon_path.is_file():
            assets.append(IconAsset(label=label, path=icon_path, is_custom=False))
    return assets


def discover_custom_icons(directory: Path = CUSTOM_ICONS_DIR) -> list[IconAsset]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        return []

    assets: list[IconAsset] = []
    for entry in sorted(directory.iterdir(), key=lambda item: humanize_filename(item.name).lower()):
        if entry.name.startswith("."):
            continue
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in ALLOWED_ICON_EXTENSIONS:
            continue
        assets.append(IconAsset(label=humanize_filename(entry.name), path=entry.resolve(), is_custom=True))
    return assets


def open_directory_in_nautilus(directory: Path | str) -> OperationResult:
    candidate = _resolve_candidate(directory)
    ensure_runtime_directories()
    if not candidate.exists():
        return OperationResult(candidate, False, "La carpeta no existe.")
    if not candidate.is_dir():
        return OperationResult(candidate, False, "La ruta no es una carpeta.")
    try:
        subprocess.Popen(["nautilus", str(candidate)])
    except Exception as exc:
        log_error(f"No se pudo abrir Nautilus en {candidate}", exc)
        return OperationResult(candidate, False, f"No se pudo abrir Nautilus: {exc}")
    return OperationResult(candidate, True, "Carpeta abierta.")


def _gio_set_custom_icon(folder_path: Path, icon_uri: str) -> None:
    gfile = Gio.File.new_for_path(str(folder_path))
    if not gfile.set_attribute_string(
        "metadata::custom-icon",
        icon_uri,
        Gio.FileQueryInfoFlags.NONE,
        None,
    ):
        raise RuntimeError("No se pudo escribir metadata::custom-icon con Gio.")


def _gio_unset_custom_icon(folder_path: Path) -> None:
    gfile = Gio.File.new_for_path(str(folder_path))
    if not gfile.set_attribute(
        "metadata::custom-icon",
        Gio.FileAttributeType.INVALID,
        None,
        Gio.FileQueryInfoFlags.NONE,
        None,
    ):
        raise RuntimeError("No se pudo eliminar metadata::custom-icon con Gio.")


def _subprocess_set_custom_icon(folder_path: Path, icon_uri: str) -> None:
    subprocess.run(
        ["gio", "set", "-t", "string", str(folder_path), "metadata::custom-icon", icon_uri],
        check=True,
        capture_output=True,
        text=True,
    )


def _subprocess_unset_custom_icon(folder_path: Path) -> None:
    subprocess.run(
        ["gio", "set", "-t", "unset", str(folder_path), "metadata::custom-icon"],
        check=True,
        capture_output=True,
        text=True,
    )


def _notify_nautilus_folder_changed(folder_path: Path) -> None:
    now = time.time()
    os.utime(folder_path, (now, now), follow_symlinks=False)


def _successful_metadata_result(
    folder_path: Path,
    message: str,
    icon_uri: str | None = None,
) -> OperationResult:
    try:
        _notify_nautilus_folder_changed(folder_path)
    except Exception as exc:
        log_error(f"No se pudo notificar a Nautilus el cambio en {folder_path}", exc)
    return OperationResult(folder_path, True, message, icon_uri)


def _apply_metadata_change(
    folder_path: Path,
    *,
    icon_uri: str | None,
    operation_name: str,
) -> OperationResult:
    if icon_uri is not None:
        try:
            _gio_set_custom_icon(folder_path, icon_uri)
            return _successful_metadata_result(folder_path, f"{operation_name} aplicado.", icon_uri)
        except Exception as exc:
            log_error(f"Falló Gio al aplicar icono en {folder_path}", exc)
            try:
                _subprocess_set_custom_icon(folder_path, icon_uri)
                return _successful_metadata_result(folder_path, f"{operation_name} aplicado.", icon_uri)
            except Exception as fallback_exc:
                log_error(f"Falló el respaldo gio set para {folder_path}", fallback_exc)
                return OperationResult(folder_path, False, f"No se pudo aplicar el icono: {fallback_exc}")

    try:
        _gio_unset_custom_icon(folder_path)
        return _successful_metadata_result(folder_path, "Icono original restaurado.")
    except Exception as exc:
        log_error(f"Falló Gio al restaurar icono en {folder_path}", exc)
        try:
            _subprocess_unset_custom_icon(folder_path)
            return _successful_metadata_result(folder_path, "Icono original restaurado.")
        except Exception as fallback_exc:
            log_error(f"Falló el respaldo gio set --unset para {folder_path}", fallback_exc)
            return OperationResult(folder_path, False, f"No se pudo restaurar el icono: {fallback_exc}")


def apply_icon_to_folder(folder_path: Path | str, icon_path: Path | str) -> OperationResult:
    folder = _resolve_candidate(folder_path)
    icon = _resolve_candidate(icon_path)

    if not folder.exists():
        return OperationResult(folder, False, "La carpeta no existe.")
    if not folder.is_dir():
        return OperationResult(folder, False, "La ruta no es una carpeta.")
    if not Gio.File.new_for_path(str(folder)).is_native():
        return OperationResult(folder, False, "La carpeta no es local.")

    if not is_supported_icon_file(icon):
        return OperationResult(folder, False, "El icono no existe o no tiene un formato compatible.")

    icon_uri = icon.resolve().as_uri()
    return _apply_metadata_change(folder, icon_uri=icon_uri, operation_name="Icono personalizado")


def restore_icon_for_folder(folder_path: Path | str) -> OperationResult:
    folder = _resolve_candidate(folder_path)
    if not folder.exists():
        return OperationResult(folder, False, "La carpeta no existe.")
    if not folder.is_dir():
        return OperationResult(folder, False, "La ruta no es una carpeta.")
    if not Gio.File.new_for_path(str(folder)).is_native():
        return OperationResult(folder, False, "La carpeta no es local.")
    return _apply_metadata_change(folder, icon_uri=None, operation_name="Restauración")


def apply_icon_to_multiple_folders(
    folder_paths: Sequence[Path | str],
    icon_path: Path | str,
) -> BatchResult:
    succeeded: list[OperationResult] = []
    failed: list[OperationResult] = []
    for folder_path in folder_paths:
        result = apply_icon_to_folder(folder_path, icon_path)
        (succeeded if result.success else failed).append(result)
    return BatchResult(tuple(succeeded), tuple(failed))


def restore_icon_for_multiple_folders(folder_paths: Sequence[Path | str]) -> BatchResult:
    succeeded: list[OperationResult] = []
    failed: list[OperationResult] = []
    for folder_path in folder_paths:
        result = restore_icon_for_folder(folder_path)
        (succeeded if result.success else failed).append(result)
    return BatchResult(tuple(succeeded), tuple(failed))


def build_failure_message(results: Sequence[OperationResult]) -> str:
    if not results:
        return ""
    lines = [f"- {result.path}: {result.message}" for result in results]
    return "\n".join(lines)


def open_custom_icons_directory() -> OperationResult:
    ensure_runtime_directories()
    try:
        CUSTOM_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return OperationResult(CUSTOM_ICONS_DIR, False, f"No se pudo crear la carpeta de iconos: {exc}")
    return open_directory_in_nautilus(CUSTOM_ICONS_DIR)


def _reset_results() -> None:
    """Internal test hook to reset the cached logger."""
    global _LOGGER
    _LOGGER = None
