Quiero que desarrolles un proyecto completo, funcional, instalable y documentado para Ubuntu Desktop 26.04 LTS, destinado a cambiar rápidamente el icono/color de carpetas desde el menú contextual de Archivos de GNOME (Nautilus).

NOMBRE DEL PROYECTO

KAFOLCOLOR

OBJETIVO PRINCIPAL

Crear una extensión para Nautilus que permita:

1. Hacer clic derecho sobre una o varias carpetas.
2. Ver una opción de menú contextual llamada “Cambiar color o icono”.
3. Dentro de esa opción, disponer de:
   - Rojo
   - Verde
   - Azul
   - Amarillo
   - Negro
   - Blanco
   - Restaurar icono original
   - Iconos personalizados
   - Abrir galería de iconos personalizados
   - Abrir carpeta de iconos personalizados
4. Aplicar inmediatamente el icono elegido a la carpeta o carpetas seleccionadas.
5. Permitir que el usuario añada sus propios iconos en un directorio determinado y pueda seleccionarlos desde el botón derecho.
6. Incluir una galería visual auxiliar para ver miniaturas de los iconos personalizados antes de aplicarlos.

CONTEXTO TÉCNICO OBLIGATORIO

El sistema objetivo es Ubuntu Desktop 26.04 LTS con GNOME, Nautilus y sesión Wayland.

No debes hacer una extensión de GNOME Shell ni una aplicación basada en X11. La integración debe realizarse mediante una extensión de Nautilus escrita en Python utilizando python3-nautilus y PyGObject.

Wayland no debe condicionar el funcionamiento porque la extensión solamente actúa dentro de Nautilus y utiliza metadatos GIO para asignar iconos.

Debes respetar la API moderna de Nautilus-python compatible con Nautilus 43 o posterior.

No utilices APIs antiguas de GTK incrustadas en Nautilus ni dependas de propiedades eliminadas o deprecadas como MenuItem.icon, MenuItem.tip o MenuItem.priority.

IMPORTANTE SOBRE LAS PREVISUALIZACIONES

La API actual de Nautilus no permite mostrar de forma fiable miniaturas de cada icono directamente dentro de los elementos del menú contextual.

Por tanto:

- En el submenú “Iconos personalizados”, muestra los iconos disponibles mediante su nombre legible.
- Incluye una acción “Abrir galería de iconos personalizados”.
- Esa acción debe abrir una pequeña aplicación GTK4 independiente, integrada visualmente con GNOME, que muestre una cuadrícula con las miniaturas reales de los iconos disponibles.
- Al seleccionar un icono desde la galería, este debe aplicarse a la carpeta o carpetas que originaron la acción.
- No simules miniaturas dentro del menú contextual ni uses APIs obsoletas.

FUNCIONAMIENTO PARA CAMBIAR ICONOS

Utiliza GIO y el atributo:

metadata::custom-icon

El icono debe asignarse mediante una URI absoluta file:// apuntando al archivo SVG o PNG correspondiente.

Comportamiento equivalente esperado:

gio set -t string "/ruta/a/carpeta" metadata::custom-icon "file:///ruta/absoluta/icono.svg"

Para restaurar el icono original:

gio set -t unset "/ruta/a/carpeta" metadata::custom-icon

No debes modificar el contenido interno de las carpetas seleccionadas. La personalización debe quedar almacenada mediante los metadatos de GNOME/Nautilus.

REQUISITOS FUNCIONALES

1. Menú contextual

La extensión solo debe mostrar “Cambiar color o icono” cuando:

- Se haya seleccionado al menos una carpeta local.
- Todos los elementos seleccionados sean carpetas.
- Las carpetas sean compatibles con la asignación de metadatos.

Si se seleccionan archivos normales, accesos remotos no compatibles o una mezcla de archivos y carpetas, no debe mostrarse el menú, o debe deshabilitarse de forma segura.

Estructura del menú:

Cambiar color o icono
├── Colores predeterminados
│   ├── Rojo
│   ├── Verde
│   ├── Azul
│   ├── Amarillo
│   ├── Negro
│   └── Blanco
├── Iconos personalizados
│   ├── [iconos encontrados en el directorio del usuario]
│   └── Actualizar lista
├── Abrir galería de iconos personalizados
├── Abrir carpeta de iconos personalizados
└── Restaurar icono original

Los textos de la interfaz deben estar en castellano.

2. Colores predeterminados

Incluye seis iconos SVG propios:

- folder-red.svg
- folder-green.svg
- folder-blue.svg
- folder-yellow.svg
- folder-black.svg
- folder-white.svg

Los iconos deben:

- Tener aspecto moderno, limpio y consistente.
- Representar claramente una carpeta.
- Funcionar correctamente tanto en modo claro como en modo oscuro.
- Mantener buen contraste en Nautilus.
- Tener un tamaño vectorial adecuado y no depender del tema de iconos instalado.
- Parecer razonablemente integrados con el estilo visual de GNOME/Yaru, sin copiar archivos protegidos ni depender de Yaru.

El icono negro debe incluir detalles o borde suficientes para ser visible en temas oscuros.
El icono blanco debe incluir borde o sombra suficiente para ser visible en temas claros.

3. Directorio de iconos personalizados

El usuario podrá colocar iconos personalizados en:

~/.local/share/folder-palette/custom-icons/

La extensión debe crear ese directorio automáticamente en la instalación o durante el primer uso.

Formatos aceptados:

- .svg
- .png
- .jpg
- .jpeg
- .webp

El sistema debe:

- Ignorar archivos ocultos.
- Ignorar subdirectorios.
- Ignorar extensiones no compatibles.
- Ordenar alfabéticamente los iconos disponibles.
- Convertir el nombre del archivo en un nombre de menú legible:
  - proyecto-importante.svg → Proyecto importante
  - clientes_2026.png → Clientes 2026
- Evitar errores si el directorio está vacío.
- Si no hay iconos personalizados, mostrar dentro del submenú una entrada deshabilitada: “No hay iconos personalizados”.

4. Abrir carpeta de iconos personalizados

La opción “Abrir carpeta de iconos personalizados” debe abrir:

~/.local/share/folder-palette/custom-icons/

en Nautilus.

Si la carpeta no existe, debe crearla antes de abrirla.

5. Galería visual de iconos

Crea una pequeña aplicación GTK4 independiente denominada:

folder-palette-gallery.py

Esta aplicación debe abrirse desde el menú contextual de Nautilus y recibir como argumentos las rutas de las carpetas seleccionadas.

La galería debe:

- Mostrar una ventana moderna y sencilla.
- Tener título “Seleccionar icono para la carpeta”.
- Si hay varias carpetas seleccionadas, usar el título “Seleccionar icono para las carpetas seleccionadas”.
- Mostrar primero los seis colores predeterminados.
- Mostrar después los iconos personalizados del usuario.
- Representar cada opción mediante:
  - Miniatura visible del icono.
  - Nombre debajo.
  - Botón o tarjeta seleccionable.
- Incluir una opción “Restaurar icono original”.
- Incluir un botón “Abrir carpeta de iconos”.
- Incluir un botón “Actualizar”.
- Permitir aplicar el icono con un solo clic.
- Cerrar la ventana automáticamente tras aplicar correctamente un icono, salvo que sea necesario mostrar un error.
- Mostrar un mensaje de error comprensible si no se puede aplicar el icono a alguna carpeta.

La galería debe utilizar GTK4 mediante PyGObject. No utilices Electron, Qt, Tkinter ni tecnologías web.

6. Aplicación sobre varias carpetas

Si el usuario selecciona varias carpetas y aplica un color o icono:

- Debe aplicarse a todas las carpetas seleccionadas.
- Si alguna falla, se deben aplicar las posibles y mostrar al usuario qué carpetas no se pudieron modificar.
- La restauración del icono original también debe funcionar sobre múltiples carpetas.

7. Persistencia y actualización

No es necesario crear una base de datos.

La extensión debe leer dinámicamente el contenido del directorio custom-icons cada vez que Nautilus construya el menú contextual o cuando el usuario pulse “Actualizar lista”.

Si el usuario añade un icono nuevo al directorio, debe poder seleccionarlo sin reinstalar la extensión.

8. Seguridad y robustez

Debes evitar:

- Ejecutar comandos de shell construidos concatenando rutas del usuario.
- Problemas con carpetas que contienen espacios, tildes o caracteres especiales.
- Aplicar iconos a rutas que no sean directorios.
- Caídas de Nautilus por excepciones sin capturar.
- Dependencias innecesarias.
- Escribir archivos dentro de las carpetas seleccionadas.
- Usar privilegios root para el funcionamiento normal.

Utiliza Gio.File, pathlib, subprocess con listas de argumentos cuando sea necesario y gestión explícita de excepciones.

La extensión debe registrar errores de forma discreta en:

~/.local/state/folder-palette/folder-palette.log

Crea la carpeta de logs si no existe.

No muestres mensajes molestos por operaciones correctas. Solo presenta errores cuando una acción no pueda completarse.

9. Instalación por usuario

La instalación normal debe ser únicamente para el usuario actual, sin copiar archivos en /usr y sin usar sudo, salvo para instalar dependencias del sistema.

Dependencias del sistema:

sudo apt install python3-nautilus python3-gi gir1.2-gtk-4.0

La estructura instalada debe ser:

~/.local/share/nautilus-python/extensions/folder_palette_extension.py
~/.local/share/folder-palette/icons/default/
~/.local/share/folder-palette/custom-icons/
~/.local/share/folder-palette/bin/folder-palette-gallery.py
~/.local/state/folder-palette/

Después de instalar, el script debe reiniciar Nautilus de forma segura mediante:

nautilus -q

No debe matar indiscriminadamente procesos ni afectar al escritorio.

10. Desinstalación

Crea un script uninstall.sh que:

- Elimine la extensión de Nautilus.
- Elimine los iconos predeterminados y la galería instalada.
- Pregunte al usuario antes de eliminar sus iconos personalizados.
- No elimine los metadatos ya aplicados sobre carpetas, porque esas carpetas podrían seguir usando iconos personalizados.
- Informe de que, si se borran los SVG usados por carpetas, las carpetas personalizadas pueden mostrar iconos rotos.
- Reinicie Nautilus al terminar.

11. Posible mejora para desinstalación

Incluye opcionalmente un script:

reset-selected-folders.py

No tiene que rastrear todas las carpetas del sistema. Solamente debe permitir al usuario ejecutar:

python3 reset-selected-folders.py /ruta/carpeta1 /ruta/carpeta2

para eliminar metadata::custom-icon de carpetas indicadas manualmente.

12. Nombre y organización del repositorio

Genera el proyecto completo con esta estructura:

folder-palette/
├── README.md
├── LICENSE
├── install.sh
├── uninstall.sh
├── run-tests.sh
├── requirements-dev.txt
├── src/
│   ├── extension/
│   │   └── folder_palette_extension.py
│   ├── gallery/
│   │   └── folder-palette-gallery.py
│   ├── common/
│   │   └── folder_palette_common.py
│   └── tools/
│       └── reset-selected-folders.py
├── assets/
│   └── icons/
│       └── default/
│           ├── folder-red.svg
│           ├── folder-green.svg
│           ├── folder-blue.svg
│           ├── folder-yellow.svg
│           ├── folder-black.svg
│           └── folder-white.svg
└── tests/
    ├── test_icon_discovery.py
    ├── test_name_formatting.py
    ├── test_path_validation.py
    └── test_metadata_operations.py

13. Arquitectura del código

Separa la lógica en tres partes:

A. folder_palette_common.py

Debe contener:

- Constantes de rutas XDG.
- Definición de iconos predeterminados.
- Función para crear directorios necesarios.
- Función para descubrir iconos personalizados.
- Función para convertir nombres de archivo en etiquetas legibles.
- Función para validar carpetas seleccionadas.
- Función para aplicar un icono mediante Gio.
- Función para restaurar icono original.
- Función para aplicar acciones a múltiples carpetas.
- Sistema de logging.
- Gestión centralizada de errores.

B. folder_palette_extension.py

Debe contener exclusivamente la integración con Nautilus:

- Clase basada en GObject.GObject y Nautilus.MenuProvider.
- Método get_file_items compatible con la API moderna.
- Detección de carpetas seleccionadas.
- Creación de los menús y submenús.
- Conexión de acciones a las funciones comunes.
- Lanzamiento seguro de la galería GTK4.
- Apertura segura del directorio custom-icons.

No metas toda la lógica en la extensión. Debe ser corta y robusta para reducir el riesgo de bloquear Nautilus.

C. folder-palette-gallery.py

Debe contener:

- Interfaz GTK4.
- Carga de iconos predeterminados y personalizados.
- Cuadrícula desplazable de iconos.
- Aplicación del icono seleccionado.
- Restauración.
- Actualización de iconos.
- Apertura del directorio custom-icons.
- Mensajes de error.

14. Uso de rutas XDG

No codifiques literalmente /home/usuario.

Utiliza las rutas adecuadas:

DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
STATE_HOME = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))

Deriva desde ellas:

APP_DATA_DIR = DATA_HOME / "folder-palette"
DEFAULT_ICONS_DIR = APP_DATA_DIR / "icons" / "default"
CUSTOM_ICONS_DIR = APP_DATA_DIR / "custom-icons"
BIN_DIR = APP_DATA_DIR / "bin"
LOG_DIR = STATE_HOME / "folder-palette"
NAUTILUS_EXTENSION_DIR = DATA_HOME / "nautilus-python" / "extensions"

15. Aplicación del icono mediante Gio

Prioriza una implementación usando PyGObject y Gio.File.

La función para aplicar un icono debe:

- Recibir una ruta de carpeta y una ruta de icono.
- Convertir ambas a rutas absolutas.
- Verificar que la carpeta existe y es directorio.
- Verificar que el icono existe y tiene formato permitido.
- Convertir el icono a URI mediante Path.as_uri().
- Escribir metadata::custom-icon como string.
- Capturar errores y devolver un resultado estructurado.

La restauración debe eliminar el atributo metadata::custom-icon.

No dependas de ejecutar `gio set` mediante shell si la operación puede hacerse correctamente desde PyGObject. Si descubres durante la implementación que la escritura de metadatos mediante Gio.File no funciona de forma fiable en esta versión, implementa un fallback controlado usando:

subprocess.run(
    ["gio", "set", "-t", "string", str(folder_path), "metadata::custom-icon", icon_uri],
    check=True,
    capture_output=True,
    text=True
)

Y para restaurar:

subprocess.run(
    ["gio", "set", "-t", "unset", str(folder_path), "metadata::custom-icon"],
    check=True,
    capture_output=True,
    text=True
)

Nunca utilices shell=True.

16. Compatibilidad y verificación inicial

Antes de dar por terminado el proyecto, detecta y documenta el entorno local real con estos comandos:

nautilus --version
python3 --version
apt policy nautilus python3-nautilus python3-gi gir1.2-gtk-4.0
echo "$XDG_SESSION_TYPE"
echo "$XDG_CURRENT_DESKTOP"

Si algún paquete no está instalado, no supongas resultados: indícalo en README.md y proporciona el comando exacto de instalación.

La aplicación debe orientarse a Ubuntu 26.04 y Wayland, pero no debe contener código dependiente de Wayland.

17. Instalador

Crea install.sh con estas características:

- Bash estricto: set -euo pipefail.
- Comprueba que existen python3 y nautilus.
- Comprueba si python3 puede importar gi y Nautilus.
- Si falta una dependencia, informa del comando exacto para instalarla y termina sin dejar instalación parcial.
- Crea las rutas XDG necesarias.
- Copia la extensión.
- Copia el módulo común de forma que la extensión y la galería puedan importarlo correctamente.
- Copia la galería.
- Copia los seis iconos predeterminados.
- Marca la galería y herramientas como ejecutables.
- Mantiene intactos los iconos personalizados existentes en reinstalaciones.
- Reinicia Nautilus al finalizar.
- Muestra un resumen claro:
  - Instalación completada.
  - Ruta para añadir iconos propios.
  - Cómo utilizar la función desde el botón derecho.
  - Cómo desinstalar.

Debes decidir la forma más robusta de distribuir el módulo común para evitar errores de importación desde la extensión de Nautilus. Puedes copiarlo junto a la extensión y también junto a la galería si es la opción más simple y fiable.

18. Pruebas

Incluye pruebas unitarias con pytest para toda la lógica que no requiera tener Nautilus abierto.

Las pruebas deben cubrir:

- Descubrimiento de iconos compatibles.
- Exclusión de archivos no compatibles.
- Exclusión de directorios y archivos ocultos.
- Formateo correcto de nombres legibles.
- Validación de carpetas.
- Aplicación y restauración de metadatos simulando Gio o subprocess con mocks.
- Tratamiento de múltiples carpetas con éxito parcial.
- Rutas con espacios y caracteres Unicode.

No intentes testear Nautilus de forma automática mediante una interfaz gráfica compleja.

Crea run-tests.sh que:

- Cree un entorno virtual `.venv` si no existe.
- Instale pytest si es necesario.
- Ejecute todos los tests.
- Muestre resultado claro.

19. Pruebas manuales obligatorias documentadas

En README.md incluye una sección de comprobación manual paso a paso:

1. Instalar dependencias.
2. Ejecutar `./install.sh`.
3. Cerrar y volver a abrir Archivos.
4. Crear una carpeta de prueba.
5. Pulsar botón derecho sobre ella.
6. Elegir “Cambiar color o icono > Colores predeterminados > Rojo”.
7. Confirmar que cambia el icono.
8. Elegir “Restaurar icono original”.
9. Copiar un SVG o PNG propio en `~/.local/share/folder-palette/custom-icons/`.
10. Pulsar botón derecho y confirmar que aparece en “Iconos personalizados”.
11. Abrir la galería visual y comprobar que aparece su miniatura.
12. Seleccionar varias carpetas y aplicar un color a todas.
13. Comprobar rutas con espacios y tildes.
14. Ejecutar la desinstalación.

Incluye también instrucciones de diagnóstico:

NAUTILUS_PYTHON_DEBUG=misc nautilus

y cómo consultar el log:

cat ~/.local/state/folder-palette/folder-palette.log

20. README.md

El README debe estar escrito en castellano y contener:

- Qué es Folder Palette.
- Captura pendiente o espacio previsto para capturas.
- Compatibilidad: Ubuntu Desktop 26.04, Nautilus y Wayland.
- Arquitectura: extensión Nautilus + galería GTK4.
- Dependencias.
- Instalación.
- Uso.
- Cómo añadir iconos personalizados.
- Cómo restaurar iconos.
- Desinstalación.
- Diagnóstico de errores.
- Limitaciones conocidas:
  - El menú contextual lista por nombre los iconos personalizados.
  - Las miniaturas se muestran en la galería visual porque la API moderna de Nautilus no soporta iconos gráficos fiables en los elementos del menú.
  - Los iconos asignados mediante metadatos son específicos del entorno GNOME/Nautilus del usuario.
- Licencia.

21. Licencia

Utiliza GPL-3.0-or-later para el proyecto completo.

Incluye un archivo LICENSE apropiado y cabeceras breves en los archivos Python principales.

22. Calidad del código

El código debe:

- Ser funcional, no pseudocódigo.
- Usar type hints siempre que sea razonable.
- Seguir una organización limpia.
- Incluir comentarios solamente donde aporten contexto técnico.
- No incluir código muerto.
- No depender de internet durante el uso.
- Evitar dependencias Python externas salvo pytest para pruebas.
- Usar únicamente bibliotecas estándar y PyGObject para ejecución.
- Mantener Nautilus estable aunque falle cualquier operación.

23. Entrega solicitada

No te limites a explicar cómo hacerlo.

Debes:

1. Crear todos los archivos del proyecto.
2. Escribir todo el código completo.
3. Crear los seis SVG funcionales.
4. Crear install.sh y uninstall.sh.
5. Crear README.md.
6. Crear tests y ejecutarlos.
7. Corregir cualquier fallo encontrado en las pruebas.
8. Mostrar al final:
   - Árbol final de archivos.
   - Comandos exactos para instalar.
   - Resultado de los tests.
   - Cualquier limitación real detectada.
9. No declares que funciona en Nautilus real si no has podido probarlo directamente en una sesión de Nautilus. En ese caso, distingue claramente entre:
   - Pruebas unitarias superadas.
   - Instalación preparada.
   - Prueba manual pendiente en Nautilus.

24. Criterios de aceptación

El proyecto se considerará terminado cuando:

- La extensión aparece en el menú contextual de Nautilus al pulsar sobre carpetas.
- Pueden aplicarse los seis colores predeterminados.
- Puede restaurarse el icono original.
- Los iconos personalizados añadidos al directorio del usuario aparecen en el menú por nombre.
- La galería muestra miniaturas reales y permite aplicar cualquier icono.
- Funciona sobre varias carpetas seleccionadas.
- No se bloquea Nautilus aunque haya errores.
- La instalación es por usuario y reversible.
- El proyecto incluye documentación y tests.
- No depende del tema de iconos instalado.
- No utiliza APIs obsoletas de Nautilus.
