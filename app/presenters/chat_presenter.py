# =============================================================================
# chat_presenter.py — Presentador MVP: orquesta Modelo ↔ Vista
# Convención: imports alfabéticos · atributos por longitud ascendente
#             métodos por longitud de nombre ascendente
# =============================================================================

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from app.models.ai_engine import AIEngine, ARCHEYPES
from app.models.image_processor import ImageProcessor

if TYPE_CHECKING:
    from app.views.main_window import MainWindow


class ChatPresenter:
    """Intermediario entre la Vista y los Modelos de IA e imagen."""

    # Atributos por longitud ascendente: view(4) · engine(6) · processor(9)
    def __init__(self, view: "MainWindow") -> None:
        self.view: "MainWindow" = view
        self.engine: AIEngine = AIEngine()
        self.processor: ImageProcessor = ImageProcessor()
        self._image = None  # PIL.Image activa
        self._responses: dict[str, str] = {}
        self._generating: bool = False
        self._active_mode: str | None = None
        self._conversation_json: dict | None = None  # JSON extraído de la imagen

    # --- on_load (7) -------------------------------------------------------
    def on_load(self, path: str) -> None:
        """Carga la imagen desde disco y actualiza la previsualización en la Vista."""
        try:
            self._image = self.processor.load(path)
            resized = self.processor.resize(self._image)
            thumbnail = self.processor.to_thumbnail(resized)
            self.view.show_preview(thumbnail)
            self.view.set_status("✅ Imagen cargada. Elige un modo de respuesta.")
            self._responses.clear()
            self._conversation_json = None  # Resetear cache JSON
            self._generating = False
            self._active_mode = None
            self.view.clear_all_modes_status()
        except (ValueError, FileNotFoundError) as exc:
            self.view.show_error(str(exc))

    # --- on_generate (11) --------------------------------------------------
    def on_generate(self, mode: str) -> None:
        """Genera respuestas para TODOS los modos en paralelo y cachea resultados."""
        if self._image is None:
            self.view.show_error("⚠️ Carga una imagen antes de generar.")
            return

        self._active_mode = mode

        # Si ya está en caché, mostrar inmediatamente
        if mode in self._responses:
            self.view.show_response(self._responses[mode])
            self.view.set_status(f"✅ Respuesta '{mode}' (precargada)")
            return

        # Si es la primera vez: extraer JSON primero, luego generar
        if not self._generating:
            self._generating = True
            self.view.set_loading(True)
            self.view.set_status("⏳ Analizando conversación…")
            threading.Thread(
                target=self._run_extraction,
                daemon=True,
            ).start()
        else:
            self.view.set_status(f"⏳ Generando '{mode}'…")

    # --- _run_extraction (16) ----------------------------------------------
    def _run_extraction(self) -> None:
        """Fase 1: extrae el JSON de la conversación y luego lanza todos los modos."""
        try:
            image_for_api = self.processor.resize(self._image)
            self._conversation_json = self.engine.extract_conversation(image_for_api)
        except Exception:  # noqa: BLE001
            self._conversation_json = None

        # Fase 2: lanzar todos los modos en paralelo
        self.view.set_status("⏳ Generando todas las respuestas…")
        for m in list(ARCHEYPES.keys()):
            if m not in self._responses:
                self.view.mark_mode_loading(m)
                threading.Thread(
                    target=self._run_generation,
                    args=(m,),
                    daemon=True,
                ).start()

    # --- _run_generation (15) ----------------------------------------------
    def _run_generation(self, mode: str) -> None:
        """Ejecuta la llamada a la IA en un hilo secundario y actualiza la Vista."""
        try:
            image_for_api = self.processor.resize(self._image)
            response = self.engine.ask(image_for_api, mode, self._conversation_json)
            self._on_success(response, mode)
        except Exception as exc:  # noqa: BLE001
            err_msg = str(exc)
            self._on_error(err_msg, mode)

    # --- _on_error (9) -----------------------------------------------------
    def _on_error(self, message: str, mode: str) -> None:
        """Maneja errores de generación en el hilo principal de la UI."""
        self._responses[mode] = f"[Error: {message}]"
        self.view.mark_mode_ready(mode)
        if mode == self._active_mode:
            self.view.set_status(f"❌ Error en '{mode}': {message}")
        if all(m in self._responses for m in ARCHEYPES):
            self._generating = False
            self.view.set_loading(False)
            self.view.set_status("❌ Algunas respuestas fallaron. Revisa tu API key.")

    # --- _on_success (10) --------------------------------------------------
    def _on_success(self, text: str, mode: str) -> None:
        """Muestra el resultado exitoso en el hilo principal de la UI."""
        self._responses[mode] = text
        self.view.mark_mode_ready(mode)
        if mode == self._active_mode:
            self.view.show_response(text)
            self.view.set_status(f"✅ Respuesta '{mode}' generada. Precargando otras…")
        if all(m in self._responses for m in ARCHEYPES):
            self._generating = False
            self.view.set_loading(False)
            self.view.set_status("✅ Todas las respuestas generadas.")
