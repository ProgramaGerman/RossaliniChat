# 💬 RossaliniChat

> _Tu copiloto de conversaciones. Analiza capturas de pantalla de chats y genera respuestas perfectas para cada situación._

![Version](https://img.shields.io/badge/version-2.1.0-7C3AED?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ¿Qué es?

**RossaliniChat** es una herramienta de escritorio que usa **inteligencia artificial multimodal** para leer capturas de pantalla de conversaciones y sugerirte la respuesta ideal. Solo sube la imagen, elige tu estilo y copia la respuesta generada.

Sin rodeos. Sin pensar demasiado. Solo resultados.

---

## Novedades v2.0.0

- 🧊 **Nuevo modo Rompehielo** — Genera mensajes creativos para iniciar conversaciones desde cero
- 👥 **Nuevo modo Amigos** — Respuestas de humor, bromas y lenguaje informal entre amigos
- 🖥️ **Panel de resoluciones** — Cambia el tamaño de ventana en tiempo real (HD / HD+ / Full HD)
- 🎨 **UI rediseñada** — Layout de 2 columnas, secciones etiquetadas y texto más visible
- ✅ **Suite de tests ampliada** — 11 pruebas unitarias (4 nuevas)

---

## Modos de Respuesta

### 💜 Modo Romántico
| Modo                 | Descripción                                    |
| -------------------- | ---------------------------------------------- |
| 🔥 **Provocativo**   | Alta tensión emocional y picardía calculada    |
| 💕 **Enamorar**      | Respuestas profundas, románticas y vulnerables |
| ⚡ **Salvada Épica** | Salidas ingeniosas para situaciones incómodas  |
| 😏 **Coquetear**     | Tono lúdico, ligero y con humor sutil          |

### 🤝 Modo Social
| Modo              | Descripción                                           |
| ----------------- | ----------------------------------------------------- |
| 🧊 **Rompehielo** | Mensajes de apertura originales para conocer a alguien |
| 👥 **Amigos**     | Humor absurdo, bromas y lenguaje informal entre amigos |

---

## Tecnologías

- **Python 3.13+** — tipado estático avanzado
- **Flet** — interfaz moderna multiplataforma con modo oscuro nativo
- **OpenRouter API** — modelos de visión multimodal (Nvidia Nemotron VL)
- **Pillow** — procesamiento de imágenes
- **httpx** — cliente HTTP asíncrono
- **python-dotenv** — gestión segura de credenciales

---

## Arquitectura

El proyecto sigue el patrón **Modelo-Vista-Presentador (MVP)**:

```
RossaliniChat/
├── app/
│   ├── models/
│   │   ├── ai_engine.py        ← 6 arquetipos de IA · OpenRouter
│   │   └── image_processor.py  ← Carga, resize y thumbnail de imágenes
│   ├── presenters/
│   │   └── chat_presenter.py   ← Orquesta Vista ↔ Modelos en hilos
│   └── views/
│       └── main_window.py      ← UI dark mode · 2 columnas · Panel config
├── tests/
│   └── test_suite.py           ← 11 pruebas unitarias (unittest)
├── main.py
├── requirements.txt
└── pyproject.toml
```

---

## Instalación

```powershell
# Clonar el repositorio
git clone https://github.com/ProgramaGerman/RossaliniChat.git
cd RossaliniChat/RossaliniChat

# Instalar dependencias
uv add flet httpx Pillow python-dotenv

# Configurar API key (crear archivo .env)
echo OPENROUTER_API_KEY=sk-or-xxxxxxxxxx > .env

# Ejecutar
uv run py main.py
```

---

## Uso

1. **Abre la app** → ventana en modo oscuro con layout de 2 paneles.
2. **Selecciona la resolución** en el panel derecho (HD / HD+ / Full HD).
3. **Haz clic en 📷 CARGAR PANTALLAZO** → selecciona tu captura de chat.
4. **Elige un modo** (🔥 💕 ⚡ 😏 🧊 👥) → la IA analiza y genera la respuesta.
5. **Copia** con 📋 COPIAR RESPUESTA y pégala donde quieras.

---

## Pruebas

```powershell
uv run python -m unittest tests/test_suite.py -v
# Ran 11 tests in ~0.2s — OK
```

---

## Changelog

### v2.1.0 — 2026-06-17
- 🛠️ **Migración a Flet** — UI multiplataforma, adiós a CustomTkinter
- 🆓 **Nuevo modelo IA** — Nvidia Nemotron VL 12B (gratuito, reemplaza a Qwen VL)
- 🐛 **Fix FilePicker** — Corrección del selector de archivos (agregado a page.overlay)
- 🔄 **max_tokens aumentado** — De 300 a 500 para respuestas más completas
- 🧹 **Limpieza** — Eliminado `.env` duplicado en `app/`

### v2.0.0 — 2026-03-15
- ✨ Nuevos modos: Rompehielo y Modo Amigos
- 🖥️ Panel lateral de resoluciones (1280×720 · 1366×768 · 1920×1080 · 1600×900)
- 🎨 Rediseño UI: layout 2 columnas, secciones etiquetadas, texto más visible
- ✅ Suite de tests ampliada a 11 pruebas

### v1.0.0 — 2026-03-01
- 🚀 Lanzamiento inicial con 4 modos: Provocativo, Enamorar, Salvada Épica, Coquetear

---

## Licencia

Proyecto personal. Todos los derechos MIT © 2026 German Gonzalez.
