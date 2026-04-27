# KrosDownloadManager

<div align="center">

**Un gestor de descargas portable para Windows, similar a Internet Download Manager (IDM)**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)

</div>

---

## Características

- **Descargas multi-hilo** — Divide cada descarga en múltiples segmentos (hasta 32 conexiones) para máxima velocidad
- **Pausar / Reanudar** — Pausa y reanuda descargas en cualquier momento sin perder el progreso
- **Cola de descargas** — Administra múltiples descargas simultáneamente con cola automática
- **Límite de velocidad** — Configura un límite de velocidad global o por descarga
- **Monitoreo del portapapeles** — Detecta automáticamente URLs en el portapapeles y ofrece descargar
- **Categorías inteligentes** — Organiza descargas por tipo: video, música, documentos, programas, etc.
- **Interfaz moderna** — GUI oscura y moderna con CustomTkinter
- **Portable** — Un solo archivo `.exe`, no requiere instalación
- **Persistencia** — Recuerda descargas y configuración entre sesiones
- **Descarga por lotes** — Agrega múltiples URLs de una vez (Ctrl+B)
- **Programación de descargas** — Programa descargas para una fecha y hora específica (Ctrl+T)
- **Verificación de integridad** — Checksums MD5 y SHA-256 automáticos al completar
- **Soporte de proxy** — Configura un proxy HTTP/HTTPS para todas las descargas
- **Bandeja del sistema** — Minimiza a la bandeja del sistema para seguir descargando en segundo plano
- **Menú contextual** — Clic derecho sobre descargas para opciones rápidas
- **Atajos de teclado** — Control completo sin soltar el teclado
- **Ícono personalizado** — Ícono de aplicación para el .exe y la barra de tareas

---

## Capturas de pantalla

La interfaz incluye:
- Barra de herramientas con acciones rápidas (nueva descarga, lotes, programar, pausar, reanudar, cancelar)
- Panel lateral con categorías, filtros y atajos de teclado
- Lista de descargas con progreso en tiempo real, velocidad y ETA
- Barra de estado con velocidad total, conteo de descargas y descargas programadas
- Menú contextual con opciones avanzadas (checksums, copiar URL, abrir carpeta)

---

## Instalación

### Opción 1: Descargar el .exe portable (Recomendado)

1. Ve a la sección [Releases](../../releases)
2. Descarga `KrosDownloadManager.exe`
3. Ejecuta el archivo — ¡no requiere instalación!

### Opción 2: Ejecutar desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/iSekro/krosdownloadmanager.git
cd krosdownloadmanager

# Instalar dependencias
pip install -e .

# Ejecutar
python -m krosdownloadmanager
```

### Opción 3: Construir el .exe tú mismo

```bash
# Instalar con dependencias de build
pip install -e ".[build]"

# Construir
python build.py
```

O en Windows, simplemente ejecuta `build.bat`.

El ejecutable portable se generará en `dist/KrosDownloadManager.exe`.

---

## Uso

### Agregar una descarga
1. Haz clic en **"+ Nueva"** o presiona **Ctrl+N**
2. Pega la URL del archivo
3. Selecciona la carpeta de destino
4. Ajusta el número de conexiones (más conexiones = más velocidad)
5. Haz clic en **"Descargar"**

### Descarga por lotes
1. Haz clic en **"Lotes"** o presiona **Ctrl+B**
2. Pega múltiples URLs (una por línea)
3. Selecciona la carpeta de destino
4. Haz clic en **"Descargar Todo"**

### Programar descarga
1. Haz clic en **"Programar"** o presiona **Ctrl+T**
2. Ingresa la URL
3. Selecciona fecha y hora
4. La descarga iniciará automáticamente a la hora programada

### Controles de descarga
- **▶ Reanudar** — Continúa una descarga pausada (Ctrl+R)
- **⏸ Pausar** — Pausa la descarga actual (Ctrl+P)
- **⏹ Cancelar** — Cancela la descarga
- **🗑 Eliminar** — Elimina la descarga de la lista (Delete)
- **▶▶ Todo** — Reanuda todas las descargas (Ctrl+A)
- **⏸⏸ Pausar Todo** — Pausa todas las descargas

### Menú contextual (clic derecho)
- Pausar / Reanudar descarga
- Cancelar descarga
- Abrir carpeta del archivo
- Ver checksums (MD5 / SHA-256)
- Copiar URL al portapapeles
- Eliminar con o sin archivo

### Atajos de teclado
| Atajo | Acción |
|-------|--------|
| Ctrl+N | Nueva descarga |
| Ctrl+B | Descarga por lotes |
| Ctrl+T | Programar descarga |
| Ctrl+P | Pausar seleccionada |
| Ctrl+R | Reanudar seleccionada |
| Ctrl+A | Reanudar todas |
| Delete | Eliminar seleccionada |
| Ctrl+Q | Salir |
| Ctrl+, | Configuración |
| F1 | Acerca de |

### Configuración
Haz clic en **"⚙ Config"** o presiona **Ctrl+,** para ajustar:
- Carpeta de descarga por defecto
- Conexiones por defecto (1-32)
- Descargas simultáneas (1-10)
- Límite de velocidad (KB/s)
- Proxy HTTP/HTTPS
- Monitoreo del portapapeles
- Minimizar a bandeja del sistema
- Tema (oscuro/claro)

---

## Arquitectura

```
src/krosdownloadmanager/
├── __init__.py
├── __main__.py          # Permite python -m krosdownloadmanager
├── main.py              # Punto de entrada principal
├── core/
│   ├── __init__.py
│   ├── config.py        # Gestión de configuración (proxy, temas, etc.)
│   └── download_engine.py  # Motor de descargas multi-hilo con checksums
├── gui/
│   ├── __init__.py
│   └── main_window.py   # Interfaz gráfica completa con bandeja del sistema
├── utils/
│   ├── __init__.py
│   └── helpers.py       # Funciones auxiliares
└── assets/
    ├── icon.ico         # Ícono para el .exe
    └── icon.png         # Ícono para la ventana
```

### Motor de descargas
- Descarga por segmentos: divide el archivo en N partes y descarga cada una en un hilo separado
- Soporte para `Range` headers HTTP para pausar/reanudar
- Reintentos automáticos (hasta 5 intentos por segmento)
- Tracker de velocidad con ventana deslizante de 2 segundos
- Fusión automática de segmentos al completar
- Verificación de integridad con MD5 y SHA-256
- Soporte de proxy HTTP/HTTPS
- Sessions HTTP con retry automático
- Programación de descargas con verificación periódica

---

## Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/ -v

# Ejecutar linter
ruff check src/

# Ejecutar la aplicación
python -m krosdownloadmanager
```

---

## Tecnologías

- **Python 3.9+** — Lenguaje principal
- **CustomTkinter** — Framework GUI moderno basado en Tkinter
- **requests** — Descargas HTTP con sessions y retry
- **threading / concurrent.futures** — Multi-hilo
- **PyInstaller** — Empaquetado portable
- **Pillow** — Procesamiento de imágenes e ícono
- **pyperclip** — Monitoreo del portapapeles
- **pystray** — Soporte de bandeja del sistema

---

## Licencia

MIT License — ver [LICENSE](LICENSE) para más detalles.

---

<div align="center">

**Hecho con ❤ por [iSekro](https://github.com/iSekro)**

</div>
