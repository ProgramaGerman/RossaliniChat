# =============================================================================
# test_suite.py — Pruebas unitarias para AIEngine e ImageProcessor
# [Revisor - Equipo Alejabot] Añadidos: TestNewModes (rompehielo + modo_amigos)
# Ejecutar: python -m pytest tests/test_suite.py -v
#       o:  python -m unittest tests/test_suite.py -v
# =============================================================================

import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_rgb_image(w: int = 400, h: int = 600) -> Image.Image:
    """Crea una imagen RGB en memoria para las pruebas."""
    return Image.new("RGB", (w, h), color=(100, 150, 200))


# ===========================================================================
# TestImageProcessor
# ===========================================================================


class TestImageProcessor(unittest.TestCase):
    """Pruebas unitarias del módulo image_processor."""

    def setUp(self) -> None:
        from app.models.image_processor import ImageProcessor

        self.proc = ImageProcessor()

    # --- test_load_invalid (16) ---
    def test_load_invalid(self) -> None:
        """Debe lanzar ValueError al cargar un archivo con extensión no permitida."""
        with self.assertRaises(ValueError):
            self.proc.load("captura.bmp")

    # --- test_load_valid (14) ---
    def test_load_valid(self) -> None:
        """Debe cargar correctamente un archivo PNG temporal válido."""
        img = _make_rgb_image()
        tmp = Path("tests/_tmp_test.png")
        img.save(tmp)
        try:
            result = self.proc.load(tmp)
            self.assertIsInstance(result, Image.Image)
        finally:
            tmp.unlink(missing_ok=True)

    # --- test_resize_bounds (17) ---
    def test_resize_bounds(self) -> None:
        """El lado más largo de la imagen redimensionada no debe superar max_px."""
        img = _make_rgb_image(2000, 3000)
        result = self.proc.resize(img, max_px=1024)
        self.assertLessEqual(max(result.size), 1024)

    # --- test_thumbnail_size (18) ---
    def test_thumbnail_size(self) -> None:
        """La miniatura debe tener exactamente el tamaño solicitado."""
        img = _make_rgb_image(800, 600)
        thumb = self.proc.to_thumbnail(img, size=(200, 200))
        self.assertEqual(thumb.size, (200, 200))


# ===========================================================================
# TestAIEngine
# ===========================================================================


class TestAIEngine(unittest.TestCase):
    """Pruebas unitarias del módulo ai_engine."""

    # --- test_missing_key (15) ---
    def test_missing_key(self) -> None:
        """AIEngine debe lanzar EnvironmentError si la key está vacía."""
        import sys

        sys.modules.pop("app.models.ai_engine", None)
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            from importlib import import_module

            eng_mod = import_module("app.models.ai_engine")
            with self.assertRaises(EnvironmentError):
                eng_mod.AIEngine()

    # --- test_invalid_mode (16) ---
    def test_invalid_mode(self) -> None:
        """Debe lanzar ValueError al pedir un modo de arquetipo desconocido."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            engine = eng_mod.AIEngine()
            img = _make_rgb_image()
            with self.assertRaises(ValueError):
                engine.ask(img, "modo_inexistente")

    # --- test_payload_structure (22) ---
    def test_payload_structure(self) -> None:
        """El payload generado debe contener las claves obligatorias para OpenRouter."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            engine = eng_mod.AIEngine()
            img = _make_rgb_image()
            payload = engine._build_payload(img, "coquetear")

            self.assertIn("model", payload)
            self.assertIn("messages", payload)
            self.assertIn("max_tokens", payload)
            self.assertIn("temperature", payload)
            self.assertIn("top_p", payload)
            self.assertTrue(len(payload["messages"]) >= 2)

    # --- test_payload_with_json (20) ---
    def test_payload_with_json(self) -> None:
        """El payload debe inyectar el JSON en el prompt si se proporciona."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            engine = eng_mod.AIEngine()
            img = _make_rgb_image()
            sample_json = {"app": "WhatsApp", "participantes": ["A", "B"]}
            payload = engine._build_payload(img, "coquetear", sample_json)

            sys_msg = payload["messages"][0]["content"]
            self.assertIn("WhatsApp", sys_msg)
            self.assertNotIn("{conversacion_json}", sys_msg)

    # --- test_extract_conversation (24) ---
    def test_extract_conversation(self) -> None:
        """extract_conversation debe construir un payload de extracción válido."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            engine = eng_mod.AIEngine()

            # Mockear _send para devolver JSON válido
            expected = {
                "app": "WhatsApp",
                "participantes": ["Alice", "Bob"],
                "conversacion": [
                    {"emisor": "Alice", "mensaje": "Hola", "hora": "10:00"}
                ],
            }
            with patch.object(engine, "_send", return_value=json.dumps(expected)):
                result = engine.extract_conversation(_make_rgb_image())
                self.assertEqual(result["app"], "WhatsApp")
                self.assertEqual(len(result["conversacion"]), 1)
                self.assertEqual(result["conversacion"][0]["emisor"], "Alice")


# ===========================================================================
# TestParseJsonResponse
# ===========================================================================


class TestParseJsonResponse(unittest.TestCase):
    """Pruebas para el parseo de JSON desde respuestas del modelo."""

    def _get_engine(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            return eng_mod.AIEngine()

    # --- test_direct_json (16) ---
    def test_direct_json(self) -> None:
        """Debe parsear JSON directo correctamente."""
        engine = self._get_engine()
        text = '{"app": "WhatsApp", "participantes": ["A"]}'
        result = engine._parse_json_response(text)
        self.assertEqual(result["app"], "WhatsApp")

    # --- test_json_in_code_block (22) ---
    def test_json_in_code_block(self) -> None:
        """Debe extraer JSON de un bloque de código markdown."""
        engine = self._get_engine()
        text = 'Aquí está el JSON:\n```json\n{"app": "Telegram"}\n```'
        result = engine._parse_json_response(text)
        self.assertEqual(result["app"], "Telegram")

    # --- test_json_in_backticks (20) ---
    def test_json_in_backticks(self) -> None:
        """Debe extraer JSON de un bloque con triple backtick sin lang."""
        engine = self._get_engine()
        text = '```\n{"app": "iMessage"}\n```'
        result = engine._parse_json_response(text)
        self.assertEqual(result["app"], "iMessage")

    # --- test_invalid_fallback (18) ---
    def test_invalid_fallback(self) -> None:
        """Debe devolver dict con error si no hay JSON parseable."""
        engine = self._get_engine()
        text = "Lo siento, no pude analizar la imagen."
        result = engine._parse_json_response(text)
        self.assertIn("error", result)

    # --- test_partial_json_braces (20) ---
    def test_partial_json_braces(self) -> None:
        """Debe extraer JSON aunque haya texto antes y después."""
        engine = self._get_engine()
        text = 'Texto antes {"app": "Signal"} texto después'
        result = engine._parse_json_response(text)
        self.assertEqual(result["app"], "Signal")


# ===========================================================================
# TestNewModes — [Revisor] Verifica los arquetipos nuevos v2.0
# ===========================================================================


class TestNewModes(unittest.TestCase):
    """Pruebas para los modos rompehielo y modo_amigos."""

    def _get_engine(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            return eng_mod.AIEngine(), eng_mod.ARCHEYPES

    # --- test_rompehielo_exists (22) ---
    def test_rompehielo_exists(self) -> None:
        """El arquetipo 'rompehielo' debe existir en ARCHEYPES."""
        engine, ARCHEYPES = self._get_engine()
        self.assertIn("rompehielo", ARCHEYPES)
        self.assertIn("primera", ARCHEYPES["rompehielo"].lower())

    # --- test_modo_amigos_exists (23) ---
    def test_modo_amigos_exists(self) -> None:
        """El arquetipo 'modo_amigos' debe existir en ARCHEYPES."""
        engine, ARCHEYPES = self._get_engine()
        self.assertIn("modo_amigos", ARCHEYPES)
        self.assertIn("amigo", ARCHEYPES["modo_amigos"].lower())

    # --- test_new_modes_payload (24) ---
    def test_new_modes_payload(self) -> None:
        """Los nuevos modos deben generar payloads válidos."""
        engine, _ = self._get_engine()
        img = _make_rgb_image()
        for mode in ("rompehielo", "modo_amigos"):
            payload = engine._build_payload(img, mode)
            self.assertIn("model", payload)
            self.assertIn("messages", payload)
            self.assertIn("temperature", payload)
            sys_msg = payload["messages"][0]
            self.assertEqual(sys_msg["role"], "system")

    # --- test_total_modes_count (25) ---
    def test_total_modes_count(self) -> None:
        """Deben existir exactamente 6 modos en ARCHEYPES."""
        _, ARCHEYPES = self._get_engine()
        self.assertEqual(len(ARCHEYPES), 6)

    # --- test_all_prompts_have_placeholder (26) ---
    def test_all_prompts_have_placeholder(self) -> None:
        """Todos los prompts deben contener el placeholder {conversacion_json}."""
        _, ARCHEYPES = self._get_engine()
        for key, prompt in ARCHEYPES.items():
            self.assertIn(
                "{conversacion_json}",
                prompt,
                f"Modo '{key}' no tiene el placeholder {{conversacion_json}}",
            )

    # --- test_mode_params_exist (27) ---
    def test_mode_params_exist(self) -> None:
        """Todos los modos deben tener parámetros definidos en MODE_PARAMS."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            for key in eng_mod.ARCHEYPES:
                self.assertIn(key, eng_mod.MODE_PARAMS)
                params = eng_mod.MODE_PARAMS[key]
                self.assertIn("temperature", params)
                self.assertIn("max_tokens", params)
                self.assertIn("top_p", params)


# ===========================================================================
# TestModeParams
# ===========================================================================


class TestModeParams(unittest.TestCase):
    """Pruebas para los parámetros por modo."""

    def test_params_values_in_range(self) -> None:
        """Temperature debe estar entre 0 y 1, max_tokens > 0."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            for mode, params in eng_mod.MODE_PARAMS.items():
                self.assertGreaterEqual(params["temperature"], 0.0)
                self.assertLessEqual(params["temperature"], 1.0)
                self.assertGreater(params["max_tokens"], 0)
                self.assertGreater(params["top_p"], 0.0)
                self.assertLessEqual(params["top_p"], 1.0)


# ===========================================================================
# TestAIEngineIntegration
# ===========================================================================


class TestAIEngineIntegration(unittest.TestCase):
    """Pruebas de integración para el pipeline completo."""

    def test_extraction_then_answer_flow(self) -> None:
        """Verifica el flujo completo: extracción + respuesta con JSON."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            from importlib import reload
            import app.models.ai_engine as eng_mod

            reload(eng_mod)
            engine = eng_mod.AIEngine()
            img = _make_rgb_image()

            with patch.object(engine, "_send") as mock_send:
                mock_send.side_effect = [
                    # Primera llamada: extracción devuelve JSON
                    json.dumps(
                        {
                            "app": "WhatsApp",
                            "participantes": ["Alice", "Bob"],
                            "tono_general": "amistoso",
                            "ultimo_mensaje": "Jajaja sí",
                            "emisor_ultimo": "Alice",
                        }
                    ),
                    # Segunda llamada: respuesta generada
                    "Claro, suena bien!",
                ]

                extracted = engine.extract_conversation(img)
                self.assertEqual(extracted["app"], "WhatsApp")

                response = engine.ask(img, "coquetear", extracted)
                self.assertEqual(response, "Claro, suena bien!")


if __name__ == "__main__":
    unittest.main()
