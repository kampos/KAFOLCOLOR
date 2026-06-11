# Registro de trabajo

Fecha: 2026-06-11

## Resumen

Se completó la extensión KAFOLCOLOR para Nautilus, se añadió refresco automático de la vista tras cambiar iconos, se preparó empaquetado Debian para Ubuntu 26.04, se generó un paquete `.deb`, y se publicó el proyecto en GitHub con una release inicial.

## Cambios realizados

### Refresco automático en Nautilus

- Se modificó `src/common/folder_palette_common.py`.
- Tras aplicar o restaurar `metadata::custom-icon`, ahora se notifica el cambio actualizando el timestamp de la carpeta con `os.utime`.
- El refresco se ejecuta tanto desde el menú contextual de Nautilus como desde la galería GTK4, porque está en la capa común.
- Si el refresco falla, el cambio de icono sigue considerándose correcto y el error queda registrado en el log.

### Pruebas

- Se ampliaron las pruebas en `tests/test_metadata_operations.py`.
- Se verificó que:
  - aplicar icono usa Gio primero;
  - restaurar icono usa Gio primero;
  - Nautilus recibe la notificación de cambio;
  - un fallo en la notificación no invalida una operación de icono exitosa;
  - los lotes de carpetas siguen recogiendo errores parciales.
- Resultado validado: `./run-tests.sh` pasa con 8 pruebas correctas.

### Empaquetado Debian

- Se añadió la carpeta `debian/` con metadatos de paquete:
  - `debian/control`
  - `debian/changelog`
  - `debian/copyright`
  - `debian/install`
  - `debian/rules`
  - `debian/source/format`
  - wrappers `folder-palette-gallery` y `folder-palette-reset`
- El paquete instala:
  - extensión Nautilus en `/usr/share/nautilus-python/extensions/`;
  - recursos y scripts en `/usr/share/folder-palette/`;
  - comandos auxiliares en `/usr/bin/`.
- Dependencias declaradas:
  - `nautilus`
  - `python3-nautilus`
  - `python3-gi`
  - `gir1.2-gtk-4.0`
  - `libglib2.0-bin`
  - `python3`
- Se generó el paquete:
  - `dist/kafolcolor_1.0.0_all.deb`

### Compatibilidad con instalación de sistema

- Se adaptaron rutas de importación para cargar el módulo común desde `/usr/share/folder-palette`.
- Los iconos predeterminados ahora pueden resolverse desde la instalación de usuario o desde `/usr/share/folder-palette/icons/default`.
- La galería y la herramienta de restauración manual también soportan la ruta de sistema.

### Documentación

- Se actualizó `README.md` con:
  - instalación por paquete Debian;
  - generación del paquete desde código fuente;
  - notas sobre la instalación de usuario.
- Se añadió `.gitignore` para excluir caches, artefactos generados, `dist/` y el repositorio Git separado local.

### Publicación en GitHub

- Se inicializó un repositorio Git local separado en `.gitrepo` porque el directorio `.git` existente estaba vacío y era de solo lectura.
- Se creó el commit inicial:
  - `9353ecb Initial release`
- Se creó el repositorio público:
  - https://github.com/kampos/KAFOLCOLOR
- Se subió la rama principal:
  - `main`
- Se creó la release:
  - https://github.com/kampos/KAFOLCOLOR/releases/tag/v1.0.0
- Se adjuntó el paquete Debian a la release:
  - `kafolcolor_1.0.0_all.deb`

## Estado final

- Proyecto publicado en GitHub.
- Release `v1.0.0` disponible con paquete `.deb`.
- Suite de pruebas pasando.
- Empaquetado Debian incluido en el repositorio.
- El archivo `.deb` local queda en `dist/`, pero `dist/` está excluido del repositorio.

## Comandos útiles

Instalar el paquete local:

```bash
sudo apt install ./dist/kafolcolor_1.0.0_all.deb
nautilus -q
```

Ejecutar pruebas:

```bash
./run-tests.sh
```

Consultar estado Git local en este workspace:

```bash
GIT_DIR=.gitrepo GIT_WORK_TREE=. git status
```
