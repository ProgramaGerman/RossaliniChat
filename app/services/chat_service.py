import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

from app.models.ai_engine import AIEngine, ARCHEYPES
from app.models.image_processor import ImageProcessor

MODE_META = {
    "coquetear": {
        "icon": "\U0001f60f",
        "label": "COQUETEAR",
        "description": "Tono lúdico, ligero y con humor sutil",
    },
    "enamorar": {
        "icon": "\U0001f495",
        "label": "ENAMORAR",
        "description": "Respuestas profundas, románticas y vulnerables",
    },
    "modo_amigos": {
        "icon": "\U0001f465",
        "label": "MODO AMIGOS",
        "description": "Humor absurdo, bromas y lenguaje informal entre amigos",
    },
    "provocativo": {
        "icon": "\U0001f525",
        "label": "PROVOCATIVO",
        "description": "Alta tensión emocional y picardía calculada",
    },
    "rompehielo": {
        "icon": "\U0001f9ca",
        "label": "ROMPEHIELO",
        "description": "Mensajes de apertura originales para conocer a alguien",
    },
    "salvada_epica": {
        "icon": "\u26a1",
        "label": "SALVADA \xc9PICA",
        "description": "Salidas ingeniosas para situaciones incómodas",
    },
}


class ChatService:
    def __init__(self) -> None:
        self.engine = AIEngine()
        self.processor = ImageProcessor()

    def get_modes(self) -> list[dict]:
        return [
            {
                "key": key,
                "icon": meta["icon"],
                "label": meta["label"],
                "description": meta["description"],
            }
            for key, meta in MODE_META.items()
        ]

    def analyze_image(self, image_bytes: bytes) -> tuple[dict, dict]:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = self.processor.resize(image)
        conversation = self.engine.extract_conversation(image)
        modes = self._generate_all(conversation)
        return modes, conversation

    def analyze_text(self, context: str) -> dict:
        conversation = {
            "context": context,
            "participantes": ["Usuario"],
            "ultimo_mensaje": context,
        }
        return self._generate_all(conversation)

    def _generate_all(self, conversation_json: dict) -> dict:
        results: dict[str, str] = {}
        for mode in ARCHEYPES:
            try:
                results[mode] = self.engine.ask_text(mode, conversation_json)
            except Exception as e:
                results[mode] = f"[Error: {e}]"
            time.sleep(3.0)
        return results
