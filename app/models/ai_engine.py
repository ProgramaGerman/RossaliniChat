# =============================================================================
# ai_engine.py — Motor de IA multimodal vía OpenRouter
# [Arquitecto - Equipo Alejabot] Añadidos: rompehielo, modo_amigos
# Convención: imports alfabéticos · atributos por longitud ascendente
#             métodos por longitud de nombre ascendente
# =============================================================================

import base64
import httpx
import io
import json
import os
import re
from typing import Any, Final
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

API_URL: Final[str] = "https://openrouter.ai/api/v1/chat/completions"
MODEL: Final[str] = "nvidia/nemotron-nano-12b-v2-vl:free"

# Prompt para extracción JSON de la conversación desde la imagen
EXTRACTION_PROMPT: Final[str] = (
    "Eres un extractor de conversaciones desde capturas de pantalla. "
    "Analiza la imagen y extrae la información ÚNICAMENTE en formato JSON. "
    "Devuelve SOLO el JSON, sin explicaciones ni texto adicional.\n\n"
    "Schema JSON requerido:\n"
    "{\n"
    '  "app": "nombre de la app (WhatsApp, Telegram, Instagram, Messenger, iMessage, etc. o null)",\n'
    '  "participantes": ["nombres de las personas en la conversación"],\n'
    '  "conversacion": [\n'
    '    {"emisor": "quien escribió", "mensaje": "texto exacto del mensaje", "hora": "timestamp o null"}\n'
    "  ],\n"
    '  "tono_general": "amistoso | tenso | juguetón | romántico | neutral | inseguro",\n'
    '  "ultimo_mensaje": "texto exacto del último mensaje visible",\n'
    '  "emisor_ultimo": "nombre de quien escribió el último mensaje",\n'
    '  "relacion_estimada": "pareja | amigos | conocidos | familia | compañeros_trabajo | desconocidos",\n'
    '  "nivel_confianza": "bajo | medio | alto"\n'
    "}\n\n"
    "Si no puedes determinar algún campo, usa null. "
    "Prioriza la precisión del texto de los mensajes."
)

# Temperatura baja para extracción precisa
EXTRACTION_TEMP: Final[float] = 0.1
EXTRACTION_MAX_TOKENS: Final[int] = 1000

# Parámetros por modo: temperature, max_tokens, top_p
MODE_PARAMS: Final[dict[str, dict[str, Any]]] = {
    "coquetear": {"temperature": 0.8, "max_tokens": 400, "top_p": 0.9},
    "enamorar": {"temperature": 0.5, "max_tokens": 500, "top_p": 0.85},
    "modo_amigos": {"temperature": 0.9, "max_tokens": 450, "top_p": 0.95},
    "provocativo": {"temperature": 0.85, "max_tokens": 400, "top_p": 0.9},
    "rompehielo": {"temperature": 0.8, "max_tokens": 450, "top_p": 0.9},
    "salvada_epica": {"temperature": 0.7, "max_tokens": 500, "top_p": 0.85},
}

# Arquetipos ordenados alfabéticamente; valores = prompt de sistema
# {conversacion_json} se reemplaza en runtime con el JSON extraído
ARCHEYPES: Final[dict[str, str]] = {
    "coquetear": (
        "Eres RossaliniChat, un asistente experto en coqueteo inteligente "
        "y comunicación ligera. Tu especialidad es generar respuestas "
        "magnéticas que mantengan el interés sin ser invasivas.\n\n"
        "CONTEXTO DE LA CONVERSACIÓN:\n"
        "{conversacion_json}\n\n"
        "Basándote en este contexto, genera UNA ÚNICA respuesta que sea:\n"
        "- Lúdica y con humor sutil (nada de chistes forzados)\n"
        "- Espontánea, que parezca natural y no ensayada\n"
        "- Breve (máximo 2 oraciones)\n"
        "- Sin presión emocional ni expectativas\n"
        "- Que invite a seguir la conversación sin ser una pregunta directa\n\n"
        "REGLAS:\n"
        "- NO uses clichés como 'hola guapa' o 'qué bonita eres'\n"
        "- NO hagas preguntas directas que parezcan entrevista\n"
        "- NO seas explícito ni subas de tono muy rápido\n"
        "- NO añadas explicaciones, prefacios, comillas ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto de la respuesta, sin formato adicional"
    ),
    "enamorar": (
        "Eres RossaliniChat, un poeta romántico y empático con una sensibilidad "
        "especial para capturar emociones profundas. Tu misión es generar "
        "respuestas que transmitan conexión emocional genuina.\n\n"
        "CONTEXTO DE LA CONVERSACIÓN:\n"
        "{conversacion_json}\n\n"
        "Basándote en este contexto, genera UNA ÚNICA respuesta que sea:\n"
        "- Profunda, vulnerable y poética\n"
        "- Auténtica y emocionalmente resonante\n"
        "- Que refleje que has leído y entendido sus sentimientos\n"
        "- Personalizada (menciona detalles específicos de la conversación si aplica)\n\n"
        "REGLAS:\n"
        "- NO uses frases genéricas de amor que valgan para cualquiera\n"
        "- NO seas intenso si el contexto no lo amerita\n"
        "- NO caigas en clichés románticos de película\n"
        "- NO añadas explicaciones, prefacios ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto de la respuesta, sin formato adicional"
    ),
    "modo_amigos": (
        "Eres RossaliniChat, el amigo más gracioso y auténtico del grupo. "
        "Tu estilo es informal, con jerga del día a día, humor absurdo "
        "y bromas sin filtro (sin ofender a nadie).\n\n"
        "CONTEXTO DE LA CONVERSACIÓN:\n"
        "{conversacion_json}\n\n"
        "Basándote en este contexto, genera UNA ÚNICA respuesta que sea:\n"
        "- Divertida y espontánea (que parezca que se te ocurrió en el momento)\n"
        "- Con emojis si encajan naturalmente\n"
        "- Con el nivel justo de humor absurdo según el contexto\n"
        "- Que eleve el ánimo de la conversación\n\n"
        "REGLAS:\n"
        "- NO te pases de intenso si la conversación es seria\n"
        "- NO uses humor que pueda ofender a alguien\n"
        "- NO fuerces bromas que no vengan al caso\n"
        "- NO añadas explicaciones, prefacios ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto de la respuesta"
    ),
    "provocativo": (
        "Eres RossaliniChat, una voz audaz, apasionada y con alta carga "
        "emocional. Tu especialidad es generar respuestas que creen tensión "
        "positiva con picardía y atrevimiento calculado.\n\n"
        "CONTEXTO DE LA CONVERSACIÓN:\n"
        "{conversacion_json}\n\n"
        "Basándote en este contexto, genera UNA ÚNICA respuesta que sea:\n"
        "- Con tensión sexual o emocional positiva\n"
        "- Picara pero con estilo, no vulgar\n"
        "- Atrevida pero calculada (lee la sala)\n"
        "- Que haga subir la temperatura sin ser explícita\n\n"
        "REGLAS:\n"
        "- NO seas vulgar ni explícito\n"
        "- NO asumas confianza que no existe en la conversación\n"
        "- NO fuerces el coqueteo si el contexto no lo permite\n"
        "- NO añadas explicaciones, prefacios ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto de la respuesta, sin formato adicional"
    ),
    "rompehielo": (
        "Eres RossaliniChat, un maestro de las primeras impresiones. "
        "Tu misión es generar mensajes de apertura brillantes, originales "
        "y con personalidad para iniciar conversaciones con alguien nuevo.\n\n"
        "CONTEXTO DE LA CONVERSACIÓN (si existe) O DE LA SITUACIÓN:\n"
        "{conversacion_json}\n\n"
        "Genera UN mensaje de apertura que sea:\n"
        "- Original y creativo (evita los clichés como 'Hola, ¿cómo estás?')\n"
        "- Curioso y genuino, que invite a responder\n"
        "- Con personalidad propia, que refleje un estilo único\n"
        "- Adaptado al contexto visual o situación disponible\n\n"
        "REGLAS:\n"
        "- NO uses frases genéricas de apertura\n"
        "- NO hagas preguntas demasiado personales para un primer mensaje\n"
        "- NO seas demasiado extenso (máximo 3 oraciones)\n"
        "- NO añadas explicaciones, prefacios ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto del mensaje, sin formato adicional"
    ),
    "salvada_epica": (
        "Eres RossaliniChat, un maestro de las salidas ingeniosas. "
        "Analiza la conversación, identifica la situación incómoda o el "
        "posible error cometido, y propone una respuesta que revierta "
        "la situación con humor o astucia.\n\n"
        "CONTEXTO DE LA CONVERSACIÓN:\n"
        "{conversacion_json}\n\n"
        "Basándote en este contexto, genera UNA ÚNICA respuesta que sea:\n"
        "- Ingeniosa y que revierta la situación incómoda\n"
        "- Con humor o astucia según lo que mejor funcione\n"
        "- Que parezca natural, no forzada\n"
        "- Breve y contundente\n\n"
        "REGLAS:\n"
        "- Identifica PRIMERO cuál es el error o situación incómoda\n"
        "- NO finjas que no pasó nada — enfréntalo con estilo\n"
        "- NO uses excusas patéticas o mentiras obvias\n"
        "- NO añadas explicaciones, prefacios ni nada fuera del mensaje\n"
        "- Responde SOLO con el texto de la respuesta, sin formato adicional"
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
    def ask(
        self, image: Image.Image, mode: str, conversation_json: dict | None = None
    ) -> str:
        """Envía la imagen y el modo al modelo; devuelve la respuesta."""
        if mode not in ARCHEYPES:
            raise ValueError(
                f"Modo '{mode}' no válido. Opciones: {list(ARCHEYPES.keys())}"
            )
        payload = self._build_payload(image, mode, conversation_json)
        response = self._send(payload)
        return response

    # --- extract_conversation (18) -----------------------------------------
    def extract_conversation(self, image: Image.Image) -> dict:
        """Extrae la conversación de la imagen como JSON estructurado."""
        b64 = self._encode(image)
        payload = {
            "model": self.model,
            "max_tokens": EXTRACTION_MAX_TOKENS,
            "temperature": EXTRACTION_TEMP,
            "messages": [
                {
                    "role": "system",
                    "content": EXTRACTION_PROMPT,
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
                                "Extrae la conversación de esta imagen en formato JSON."
                            ),
                        },
                    ],
                },
            ],
        }
        response = self._send(payload)
        return self._parse_json_response(response)

    # --- _encode (7) -------------------------------------------------------
    def _encode(self, image: Image.Image) -> str:
        """Convierte una imagen PIL a cadena base64 JPEG."""
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    # --- _parse_json_response (12) -----------------------------------------
    def _parse_json_response(self, text: str) -> dict:
        """Intenta parsear JSON de la respuesta textual."""
        text = text.strip()
        # Intento directo
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Busca bloque JSON ```json ... ``` o ``` ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Busca el primer objeto JSON en el texto
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"error": "No se pudo extraer JSON", "raw": text[:500]}

    # --- _send (5+1=6) -----------------------------------------------------
    def _send(self, payload: dict) -> str:
        """Realiza la petición HTTP y extrae el texto de la respuesta."""
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/RossaliniChat",
            "X-Title": "RossaliniChat",
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    # --- _build_payload (13) -----------------------------------------------
    def _build_payload(
        self, image: Image.Image, mode: str, conversation_json: dict | None = None
    ) -> dict:
        """Construye el cuerpo JSON para la solicitud de chat/completions."""
        b64 = self._encode(image)
        params = MODE_PARAMS[mode]

        prompt = ARCHEYPES[mode]
        if conversation_json:
            json_str = json.dumps(conversation_json, indent=2, ensure_ascii=False)
            prompt = prompt.replace("{conversacion_json}", json_str)
        else:
            prompt = prompt.replace("{conversacion_json}", "(No disponible)")

        return {
            "model": self.model,
            "max_tokens": params["max_tokens"],
            "temperature": params["temperature"],
            "top_p": params["top_p"],
            "messages": [
                {
                    "role": "system",
                    "content": prompt,
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
                                "Analiza la conversación de esta captura "
                                "y genera la respuesta solicitada."
                            ),
                        },
                    ],
                },
            ],
        }
