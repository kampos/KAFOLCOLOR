# KAFOLCOLOR

Extensión de Nautilus para cambiar rápidamente el icono o color de carpetas desde el menú contextual en GNOME/Nautilus.

## Qué hace

- Añade el submenú `Cambiar color o icono` al hacer clic derecho sobre carpetas locales.
- Permite aplicar seis iconos predeterminados: rojo, verde, azul, amarillo, negro y blanco.
- Descubre iconos personalizados en `~/.local/share/folder-palette/custom-icons/`.
- Abre una galería GTK4 independiente para ver miniaturas reales antes de aplicar un icono.
- Usa `metadata::custom-icon` y no modifica el contenido de las carpetas.

## Entorno local verificado

Comandos ejecutados en esta máquina:

- `python3 --version` -> `Python 3.14.4`
- `apt policy nautilus python3-nautilus python3-gi gir1.2-gtk-4.0`
  - `nautilus` instalado: `1:50.0-0ubuntu2`
  - `python3-nautilus` no instalado
  - `python3-gi` instalado: `3.56.2-1`
  - `gir1.2-gtk-4.0` instalado: `4.22.2+ds-1ubuntu1`
- `echo "$XDG_SESSION_TYPE"` -> `wayland`
- `echo "$XDG_CURRENT_DESKTOP"` -> `ubuntu:GNOME`

El comando `nautilus --version` no pudo completarse en esta sesión sin servidor gráfico; Nautilus intentó abrir el display y falló. El paquete disponible en APT es `1:50.0-0ubuntu2`.

Instalación de dependencias del sistema que falta en este entorno:

```bash
sudo apt install python3-nautilus python3-gi gir1.2-gtk-4.0
```

## Estructura instalada

La instalación de usuario copia los archivos en:

- `~/.local/share/nautilus-python/extensions/folder_palette_extension.py`
- `~/.local/share/folder-palette/icons/default/`
- `~/.local/share/folder-palette/custom-icons/`
- `~/.local/share/folder-palette/bin/folder-palette-gallery.py`
- `~/.local/state/folder-palette/`

## Instalación

### Paquete Debian

Para Ubuntu 26.04, el método recomendado es instalar el paquete `.deb`:

```bash
sudo apt install ./dist/kafolcolor_1.0.0_all.deb
nautilus -q
```

El paquete instala la extensión en `/usr/share/nautilus-python/extensions/`, los recursos en `/usr/share/folder-palette/` y declara las dependencias de Nautilus, GTK4 y PyGObject.

Para generar el paquete desde el código fuente:

```bash
dpkg-buildpackage -us -uc -b
```

En entornos donde no se pueda escribir el artefacto en el directorio padre del proyecto, también se puede construir el `.deb` desde el árbol preparado por `debhelper` con `dpkg-deb`.

### Instalación de usuario

1. Instala las dependencias del sistema si aún no están presentes:

   ```bash
   sudo apt install python3-nautilus python3-gi gir1.2-gtk-4.0
   ```

2. Ejecuta el instalador de usuario:

   ```bash
   ./install.sh
   ```

3. Si Nautilus estaba abierto, el instalador ejecuta `nautilus -q` para recargar la extensión.

## Uso

- Clic derecho sobre una o varias carpetas.
- Abrir `Cambiar color o icono`.
- Elegir un color, un icono personalizado o abrir la galería.
- Para iconos personalizados, coloca archivos `.svg`, `.png`, `.jpg`, `.jpeg` o `.webp` en:

  ```text
  ~/.local/share/folder-palette/custom-icons/
  ```

## Galería

La galería GTK4 se instala como `folder-palette-gallery.py` y recibe las rutas de las carpetas seleccionadas. Muestra primero los seis colores predeterminados, después los iconos personalizados y una acción de restauración.

## Desinstalación

```bash
./uninstall.sh
```

La desinstalación elimina la extensión, la galería instalada y los iconos predeterminados. Antes de borrar `custom-icons/` pregunta al usuario. No elimina los metadatos ya aplicados sobre carpetas.

## Restauración manual

Para eliminar `metadata::custom-icon` de carpetas concretas:

```bash
python3 src/tools/reset-selected-folders.py /ruta/carpeta1 /ruta/carpeta2
```

## Pruebas

```bash
./run-tests.sh
```
