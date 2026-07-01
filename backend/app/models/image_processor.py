# =============================================================================
# image_processor.py — Carga, redimensiona y genera miniaturas de imágenes
# Convención: imports alfabéticos · atributos por longitud ascendente
#             métodos por longitud de nombre ascendente
# =============================================================================

import os
from pathlib import Path
from PIL import Image

# Formatos permitidos (ordenados alfabéticamente)
ALLOWED: frozenset[str] = frozenset({".jpg", ".jpeg", ".png"})


class ImageProcessor:
    """Gestiona la carga y transformación de imágenes para la app."""

    # Atributos por longitud ascendente: fmt(3) · size(4) · max_px(5)
    def __init__(self) -> None:
        self.fmt: tuple[int, int]  = (200, 200)
        self.size: str             = "JPEG"
        self.max_px: int           = 1024

    # --- load (4) ----------------------------------------------------------
    def load(self, path: str | Path) -> Image.Image:
        """Abre y valida un archivo de imagen JPG o PNG."""
        p = Path(path)
        if p.suffix.lower() not in ALLOWED:
            raise ValueError(
                f"Formato no soportado: '{p.suffix}'. "
                f"Usa: {sorted(ALLOWED)}"
            )
        if not p.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {p}")
        return Image.open(p).convert("RGB")

    # --- resize (6) --------------------------------------------------------
    def resize(self, image: Image.Image, max_px: int | None = None) -> Image.Image:
        """Reduce la imagen proporcionalmente al máximo de píxeles indicado."""
        limit = max_px or self.max_px
        w, h  = image.size
        if max(w, h) <= limit:
            return image
        ratio   = limit / max(w, h)
        new_w   = int(w * ratio)
        new_h   = int(h * ratio)
        return image.resize((new_w, new_h), Image.LANCZOS)

    # --- to_thumbnail (12) -------------------------------------------------
    def to_thumbnail(
        self, image: Image.Image, size: tuple[int, int] | None = None
    ) -> Image.Image:
        """Genera una copia de la imagen recortada como miniatura cuadrada."""
        target   = size or self.fmt
        thumb    = image.copy()
        thumb.thumbnail(target, Image.LANCZOS)
        # Pad a canvas exacto para que la UI siempre reciba el mismo tamaño
        canvas   = Image.new("RGB", target, (13, 17, 23))   # navbar background
        offset_x = (target[0] - thumb.width)  // 2
        offset_y = (target[1] - thumb.height) // 2
        canvas.paste(thumb, (offset_x, offset_y))
        return canvas
