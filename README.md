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

---

## Capturas de pantalla

La interfaz incluye:
- Barra de herramientas con acciones rápidas (nueva descarga, pausar, reanudar, cancelar)
- Panel lateral con categorías y filtros
- Lista de descargas con progreso en tiempo real, velocidad y ETA
- Barra de estado con velocidad total y conteo de descargas

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
1. Haz clic en **"+ Nueva"** en la barra de herramientas
2. Pega la URL del archivo
3. Selecciona la carpeta de destino
4. Ajusta el número de conexiones (más conexiones = más velocidad)
5. Haz clic en **"Descargar"**

### Controles de descarga
- **▶ Reanudar** — Continúa una descarga pausada
- **⏸ Pausar** — Pausa la descarga actual
- **⏹ Cancelar** — Cancela la descarga
- **🗑 Eliminar** — Elimina la descarga de la lista
- **▶▶ Todo** — Reanuda todas las descargas
- **⏸⏸ Pausar Todo** — Pausa todas las descargas

### Configuración
Haz clic en **"⚙ Config"** para ajustar:
- Carpeta de descarga por defecto
- Conexiones por defecto (1-32)
- Descargas simultáneas (1-10)
- Límite de velocidad (KB/s)
- Monitoreo del portapapeles
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
│   ├── config.py        # Gestión de configuración
│   └── download_engine.py  # Motor de descargas multi-hilo
├── gui/
│   ├── __init__.py
│   └── main_window.py   # Interfaz gráfica completa
├── utils/
│   ├── __init__.py
│   └── helpers.py       # Funciones auxiliares
└── assets/              # Recursos gráficos
```

### Motor de descargas
- Descarga por segmentos: divide el archivo en N partes y descarga cada una en un hilo separado
- Soporte para `Range` headers HTTP para pausar/reanudar
- Reintentos automáticos (hasta 5 intentos por segmento)
- Tracker de velocidad con ventana deslizante de 2 segundos
- Fusión automática de segmentos al completar

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
- **requests** — Descargas HTTP
- **threading / concurrent.futures** — Multi-hilo
- **PyInstaller** — Empaquetado portable
- **Pillow** — Procesamiento de imágenes
- **pyperclip** — Monitoreo del portapapeles

---

## Licencia

MIT License — ver [LICENSE](LICENSE) para más detalles.

---

<div align="center">

**Hecho con ❤️ por [iSekro](https://github.com/iSekro)**

</div>
