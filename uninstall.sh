#!/usr/bin/env bash
set -euo pipefail

DATA_HOME="${XDG_DATA_HOME:-"$HOME/.local/share"}"
STATE_HOME="${XDG_STATE_HOME:-"$HOME/.local/state"}"

APP_DATA_DIR="$DATA_HOME/folder-palette"
DEFAULT_ICONS_DIR="$APP_DATA_DIR/icons/default"
CUSTOM_ICONS_DIR="$APP_DATA_DIR/custom-icons"
BIN_DIR="$APP_DATA_DIR/bin"
LOG_DIR="$STATE_HOME/folder-palette"
NAUTILUS_EXTENSION_DIR="$DATA_HOME/nautilus-python/extensions"

remove_if_exists() {
  local path="$1"
  if [ -e "$path" ]; then
    rm -rf "$path"
  fi
}

main() {
  remove_if_exists "$NAUTILUS_EXTENSION_DIR/folder_palette_extension.py"
  remove_if_exists "$BIN_DIR/folder-palette-gallery.py"
  remove_if_exists "$BIN_DIR/folder_palette_common.py"
  remove_if_exists "$BIN_DIR/reset-selected-folders.py"
  remove_if_exists "$DEFAULT_ICONS_DIR"

  printf '%s\n' "Los metadatos aplicados en carpetas no se eliminan."
  printf '%s\n' "Si borras los SVG usados por carpetas personalizadas, esas carpetas pueden mostrar iconos rotos."
  printf '%s' "¿Eliminar también tus iconos personalizados de $CUSTOM_ICONS_DIR? [y/N] "
  read -r answer
  case "${answer:-}" in
    y|Y|yes|YES)
      remove_if_exists "$CUSTOM_ICONS_DIR"
      ;;
  esac

  nautilus -q || true

  cat <<EOF
Desinstalación completada.
Se ha conservado la carpeta de logs en: $LOG_DIR
EOF
}

main "$@"

