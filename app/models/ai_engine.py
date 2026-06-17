# =============================================================================
# ai_engine.py — Motor de IA multimodal vía OpenRouter
# [Arquitecto - Equipo Alejabot] Añadidos: rompehielo, modo_amigos
# Convención: imports alfabéticos · atributos por longitud ascendente
#             métodos por longitud de nombre ascendente
# =============================================================================

import base64
import httpx
import io
import os
from typing import Final
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

API_URL: Final[str] = "https://openrouter.ai/api/v1/chat/completions"
MODEL: Final[str] = "nvidia/nemotron-nano-12b-v2-vl:free"

# Arquetipos ordenados alfabéticamente; valores = prompt de sistema
ARCHEYPES: Final[dict[str, str]] = {
    "coquetear": (
        "Eres un experto en comunicación ligera y seductora. "
        "Analiza este chat y propone UNA respuesta lúdica, con humor sutil, "
        "sin presión emocional. Sé breve, espontáneo y divertido. "
        "Responde solo con el mensaje sugerido, sin explicaciones."
    ),
    "enamorar": (
        "Eres un poeta romántico y empático. "
        "Analiza este chat y propone UNA respuesta profunda, vulnerable y poética "
        "que transmita conexión emocional genuina. "
        "Responde solo con el mensaje sugerido, sin explicaciones."
    ),
    "modo_amigos": (
        "Eres el amigo más gracioso del grupo. Tu estilo es informal, "
        "con jerga del día a día, humor absurdo, memes y bromas sin filtro (sin ofender). "
        "Analiza esta conversación entre amigos y propone UNA respuesta que haga reír, "
        "bromear o que sea épicamente divertida. "
        "Usa emojis si encajan. Responde solo con el mensaje sugerido, sin explicaciones."
    ),
    "provocativo": (
        "Eres audaz, apasionado y con alta carga emocional. "
        "Analiza este chat y propone UNA respuesta que genere tensión sexual o "
        "emocional positiva, con picardía y atrevimiento calculado. "
        "Responde solo con el mensaje sugerido, sin explicaciones."
    ),
    "rompehielo": (
        "Eres un maestro de las primeras impresiones y conversaciones nuevas. "
        "Tu misión: generar UN mensaje de apertura brillante, original y con personalidad "
        "para iniciar una conversación con alguien nuevo. "
        "Evita los clichés ('Hola, ¿cómo estás?'). Sé creativo, curioso y genuino. "
        "Si hay una imagen de perfil o contexto visual disponible, úsalo como inspiración. "
        "Responde solo con el mensaje sugerido, sin explicaciones."
    ),
    "salvada_epica": (
        "Eres un maestro de las salidas ingeniosas. "
        "Analiza este chat, identifica la situación incómoda o el error cometido "
        "y propone UNA respuesta brillante que revierta la situación con humor "
        "o astucia. Responde solo con el mensaje sugerido, sin explicaciones."
    ),
}


# ---------------------------------------------------------------------------
# Clase AIEngine
# ---------------------------------------------------------------------------


class AIEngine:
    """Gestiona las llamadas multimodales a la API de OpenRouter."""

    # Atributos ordenados por longitud ascendente: key(3) · model(5) · api_url(7)
    def __init__(self) -> None:
        self.key: str = os.environ.get("OPENROUTER_API_KEY", "")
        self.model: str = MODEL
        self.api_url: str = API_URL

        if not self.key:
            raise EnvironmentError(
                "OPENROUTER_API_KEY no encontrada. Crea un archivo .env con tu clave."
            )

    # --- ask (3) -----------------------------------------------------------
    def ask(self, image: Image.Image, mode: str) -> str:
        """Envía la imagen y el modo al modelo; devuelve la respuesta en texto."""
        if mode not in ARCHEYPES:
            raise ValueError(
                f"Modo '{mode}' no válido. Opciones: {list(ARCHEYPES.keys())}"
            )
        payload = self._build_payload(image, mode)
        response = self._send(payload)
        return response

    # --- _encode (7) -------------------------------------------------------
    def _encode(self, image: Image.Image) -> str:
        """Convierte una imagen PIL a cadena base64 JPEG."""
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    # --- _send (5+1=6) -----------------------------------------------------
    def _send(self, payload: dict) -> str:
        """Realiza la petición HTTP y extrae el texto de la respuesta."""
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/BroChaperonAI",
            "X-Title": "BroChaperonAI",
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    # --- _build_payload (13) -----------------------------------------------
    def _build_payload(self, image: Image.Image, mode: str) -> dict:
        """Construye el cuerpo JSON para la solicitud de chat/completions."""
        b64 = self._encode(image)
        return {
            "model": self.model,
            "max_tokens": 500,
            "messages": [
                {
                    "role": "system",
                    "content": ARCHEYPES[mode],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Analiza la conversación de esta captura de pantalla "
                                "y genera la respuesta solicitada."
                            ),
                        },
                    ],
                },
            ],
        }
