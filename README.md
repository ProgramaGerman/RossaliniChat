# RossaliniChat API

> _Backend API para generar respuestas de chat con IA según 6 arquetipos de interacción._

![Version](https://img.shields.io/badge/version-0.2.0-7C3AED?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ¿Qué es?

**RossaliniChat API** es un backend REST que usa **inteligencia artificial multimodal** (OpenRouter + Nvidia Nemotron VL) para analizar capturas de pantalla de conversaciones y generar respuestas en 6 modos distintos. Diseñado como backend para una futura web app.

---

## Endpoints

### `POST /api/analyze`
Analiza una captura de pantalla y genera respuestas en los 6 modos.

- **Content-Type:** `multipart/form-data`
- **Body:** `image` (archivo PNG/JPG)
- **Response:**
```json
{
  "modes": {
    "provocativo": "...",
    "enamorar": "...",
    "salvada_epica": "...",
    "coquetear": "...",
    "rompehielo": "...",
    "modo_amigos": "..."
  },
  "conversation": { "...": "..." },
  "context": null
}
```

### `POST /api/analyze/text`
Genera respuestas a partir de un contexto textual (sin imagen).

- **Content-Type:** `application/json`
- **Body:** `{ "context": "texto de la conversación..." }`
- **Response:** `{ modes: {...}, context: "...", conversation: null }`

### `GET /api/modes`
Lista los modos de respuesta disponibles.

### `GET /health`
Health check.

---

## Modos de Respuesta

| Modo | Icono | Descripción |
|------|-------|-------------|
| Provocativo | 🔥 | Alta tensión emocional y picardía calculada |
| Enamorar | 💕 | Respuestas profundas, románticas y vulnerables |
| Salvada Épica | ⚡ | Salidas ingeniosas para situaciones incómodas |
| Coquetear | 😏 | Tono lúdico, ligero y con humor sutil |
| Rompehielo | 🧊 | Mensajes de apertura originales |
| Modo Amigos | 👥 | Humor absurdo e informal entre amigos |

---

## Tecnologías

- **Python 3.13+** — tipado estático avanzado
- **FastAPI** — framework REST async
- **OpenRouter API** — modelos de visión multimodal (Nvidia Nemotron VL)
- **Pillow** — procesamiento de imágenes
- **httpx** — cliente HTTP
- **Uvicorn** — servidor ASGI

---

## Arquitectura

```
RossalinChat/
├── app/
│   ├── api/
│   │   ├── routes.py       ← Endpoints REST
│   │   └── schemas.py      ← Pydantic models
│   ├── core/
│   │   └── config.py       ← Settings (OPENROUTER_API_KEY)
│   ├── models/
│   │   ├── ai_engine.py    ← 6 arquetipos de IA · OpenRouter
│   │   └── image_processor.py
│   ├── services/
│   │   └── chat_service.py ← Lógica de negocio
│   └── main.py             ← Entrypoint FastAPI
├── tests/
│   └── test_suite.py       ← 36 pruebas unitarias (unittest)
├── pyproject.toml
└── requirements.txt
```

---

## Instalación

```powershell
git clone https://github.com/ProgramaGerman/RossaliniChat.git
cd RossaliniChat

uv sync

echo OPENROUTER_API_KEY=sk-or-xxxxxxxxxx > .env

uv run uvicorn app.main:app --reload
```

---

## Pruebas

```powershell
uv run python -m unittest tests/test_suite.py -v
# Ran 36 tests — OK
```

---

## Docker

```powershell
docker build -t rossalinichat-api .
docker run -p 8000:8000 --env-file .env rossalinichat-api
```

---

## Changelog

### v0.2.0 — 2026-06-27
- Migración de desktop app a backend API REST
- FastAPI con CORS para futura integración web
- Endpoints: `/api/analyze`, `/api/analyze/text`, `/api/modes`, `/health`
- Los 6 modos se generan en paralelo con `ThreadPoolExecutor`
- 36 tests, todos pasando

---

## Licencia

MIT © 2026 German Gonzalez.
