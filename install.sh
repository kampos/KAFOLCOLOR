#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_HOME="${XDG_DATA_HOME:-"$HOME/.local/share"}"
STATE_HOME="${XDG_STATE_HOME:-"$HOME/.local/state"}"

APP_DATA_DIR="$DATA_HOME/folder-palette"
DEFAULT_ICONS_DIR="$APP_DATA_DIR/icons/default"
CUSTOM_ICONS_DIR="$APP_DATA_DIR/custom-icons"
BIN_DIR="$APP_DATA_DIR/bin"
LOG_DIR="$STATE_HOME/folder-palette"
NAUTILUS_EXTENSION_DIR="$DATA_HOME/nautilus-python/extensions"

check_dependencies() {
  if ! python3 - <<'PY'
import gi
for version in ("4.1", "4.0"):
    try:
        gi.require_version("Nautilus", version)
        break
    except ValueError:
        continue
gi.require_version("Gtk", "4.0")
from gi.repository import Nautilus, Gtk  # noqa: F401
PY
  then
    cat <<'EOF'
Faltan dependencias del sistema.
Instala primero:
sudo apt install python3-nautilus python3-gi gir1.2-gtk-4.0
EOF
    exit 1
  fi
}

install_file() {
  local source="$1"
  local target="$2"
  install -Dm755 "$source" "$target"
}

copy_icon_set() {
  mkdir -p "$DEFAULT_ICONS_DIR"
  for icon in folder-red.svg folder-green.svg folder-blue.svg folder-yellow.svg folder-black.svg folder-white.svg; do
    install -Dm644 "$SCRIPT_DIR/assets/icons/default/$icon" "$DEFAULT_ICONS_DIR/$icon"
  done
}

main() {
  check_dependencies

  mkdir -p "$NAUTILUS_EXTENSION_DIR" "$CUSTOM_ICONS_DIR" "$BIN_DIR" "$LOG_DIR"
  copy_icon_set
  install_file "$SCRIPT_DIR/src/extension/folder_palette_extension.py" "$NAUTILUS_EXTENSION_DIR/folder_palette_extension.py"
  install_file "$SCRIPT_DIR/src/gallery/folder-palette-gallery.py" "$BIN_DIR/folder-palette-gallery.py"
  install_file "$SCRIPT_DIR/src/common/folder_palette_common.py" "$BIN_DIR/folder_palette_common.py"
  install_file "$SCRIPT_DIR/src/tools/reset-selected-folders.py" "$BIN_DIR/reset-selected-folders.py"

  nautilus -q || true

  cat <<EOF
Instalación completada.
Extensión instalada en: $NAUTILUS_EXTENSION_DIR
Galería instalada en: $BIN_DIR/folder-palette-gallery.py
Iconos por defecto instalados en: $DEFAULT_ICONS_DIR
Iconos personalizados en: $CUSTOM_ICONS_DIR
EOF
}

main "$@"
