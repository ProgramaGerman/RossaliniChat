# =============================================================================
# main_window.py — Vista principal BroChaperonAI en Flet
# =============================================================================

import base64
import threading
import tkinter as tk
from io import BytesIO
from tkinter import filedialog
from typing import TYPE_CHECKING
import flet as ft
from PIL import Image

if TYPE_CHECKING:
    from app.presenters.chat_presenter import ChatPresenter

# ---------------------------------------------------------------------------
# Nueva Paleta de Colores (Cyberpunk Indigo & Emerald)
# ---------------------------------------------------------------------------
BG_ROOT: str = "#0B0F19"  # Azul oscuro cibernético profundo
BG_CARD: str = "#1E293B"  # Tarjetas (azul marino pizarra)
BG_CARD2: str = "#0F172A"  # Zonas de respuesta y upload
BG_SIDEBAR: str = "#0F172A"  # Fondo del panel lateral
BORDER_OFF: str = "#334155"  # Borde inactivo
BORDER_ON: str = "#10B981"  # Borde activo / seleccionado (esmeralda neón)
ACCENT_DIM: str = "#059669"
TXT_MAIN: str = "#F8FAFC"  # Texto principal brillante
TXT_MID: str = "#94A3B8"  # Texto medio
TXT_DIM: str = "#64748B"  # Texto tenue
TXT_SECTION: str = "#38BDF8"  # Títulos de sección (celeste brillante)
WHITE: str = "#FFFFFF"

# Resoluciones disponibles
RESOLUTIONS = [
    ("1280×720  HD", 1280, 720),
    ("1366×768  HD+", 1366, 768),
    ("1920×1080  Full HD", 1920, 1080),
    ("1600×900  HD+", 1600, 900),
]
DEFAULT_RES_IDX: int = 2

MODE_ICONS: dict[str, str] = {
    "provocativo": "🔥",
    "enamorar": "💕",
    "salvada_epica": "⚡",
    "coquetear": "😏",
    "rompehielo": "🧊",
    "modo_amigos": "👥",
}

MODE_LABELS: dict[str, str] = {
    "provocativo": "PROVOCATIVO",
    "enamorar": "ENAMORAR",
    "salvada_epica": "SALVADA ÉPICA",
    "coquetear": "COQUETEAR",
    "rompehielo": "ROMPEHIELO",
    "modo_amigos": "MODO AMIGOS",
}

MODES_ROW1: list[str] = ["provocativo", "enamorar", "salvada_epica", "coquetear"]
MODES_ROW2: list[str] = ["rompehielo", "modo_amigos"]


class MainWindow:
    """Vista principal de BroChaperonAI adaptada a Flet con diseño moderno."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.presenter: "ChatPresenter | None" = None
        self._active_mode: str | None = None
        self._active_res_idx: int = DEFAULT_RES_IDX

        # Elementos dinámicos que actualizaremos
        self.upload_img_control = ft.Text(
            "📷", size=38, color=TXT_MID, weight=ft.FontWeight.BOLD
        )
        self.upload_title_control = ft.Text(
            "CARGAR PANTALLAZO", size=14, color=TXT_MAIN, weight=ft.FontWeight.BOLD
        )
        self.upload_sub_control = ft.Text(
            "Haz clic para seleccionar tu captura de pantalla", size=10, color=TXT_MID
        )
        self.progress_bar = ft.ProgressBar(
            value=None, color=BORDER_ON, height=2, visible=False
        )
        self.response_text = ft.Text(
            '""', size=15, italic=True, color=TXT_MAIN, selectable=True
        )
        self.status_text = ft.Text("", size=9, color=TXT_DIM)

        # Referencias de controles para modos y resolución
        self.mode_containers: dict[str, ft.Container] = {}
        self.mode_status_texts: dict[str, ft.Text] = {}
        self.res_containers: list[ft.Container] = []

    def set_presenter(self, presenter: "ChatPresenter") -> None:
        self.presenter = presenter

    def update(self) -> None:
        """Helper para actualizar la página de Flet de forma segura."""
        self.page.update()

    def show_error(self, msg: str) -> None:
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("BroChaperonAI", color=TXT_MAIN),
            content=ft.Text(msg, color=TXT_MAIN),
            actions=[
                ft.TextButton(
                    "Aceptar",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(color=BORDER_ON),
                )
            ],
            bgcolor=BG_CARD,
        )
        self.page.dialog.open = True
        self.page.update()

    def set_status(self, text: str) -> None:
        self.status_text.value = text
        self.page.update()

    def show_preview(self, image: Image.Image) -> None:
        # Convertir la imagen PIL a Base64 para mostrarla directamente en Flet sin guardarla en disco
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Actualizar los controles de carga
        self.upload_img_control = ft.Image(
            src=f"data:image/png;base64,{img_str}",
            width=68,
            height=68,
            fit="contain",
        )
        # Re-emplazar el contenido de la zona de subida
        self.upload_title_control.value = "PANTALLAZO CARGADO ✓"
        self.upload_sub_control.value = "Motor de análisis listo"
        self._build_upload_container()
        self.page.update()

    def show_response(self, text: str) -> None:
        self.response_text.value = f'"{text}"'
        self.page.update()

    def set_loading(self, active: bool) -> None:
        self.progress_bar.visible = active
        self.page.update()

    def mark_mode_loading(self, mode: str) -> None:
        if mode in self.mode_status_texts:
            self.mode_status_texts[mode].value = "⏳"
            self.page.update()

    def mark_mode_ready(self, mode: str) -> None:
        if mode in self.mode_status_texts:
            self.mode_status_texts[mode].value = "✅"
            self.page.update()

    def clear_all_modes_status(self) -> None:
        for status in self.mode_status_texts.values():
            status.value = ""
        self.page.update()

    def build_ui(self) -> None:
        """Configura y crea la estructura visual de Flet."""
        self.page.title = "BroChaperonAI"
        self.page.bgcolor = BG_ROOT

        # Aplicar tamaño inicial
        _, w, h = RESOLUTIONS[self._active_res_idx]
        self.page.window.width = w
        self.page.window.height = h
        self.page.window.min_width = 900
        self.page.window.min_height = 680

        # Contenedor para la zona de carga (se actualizará dinámicamente)
        self.upload_area = ft.Container(
            border_radius=16,
            bgcolor=BG_CARD2,
            border=ft.Border.all(1, BORDER_OFF),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=self._on_upload_click,
        )
        self._build_upload_container()

        # Layout del cuerpo (2 columnas)
        main_layout = ft.Row(
            expand=True,
            spacing=16,
            controls=[
                # Columna Izquierda (Principal)
                ft.Column(
                    expand=7,
                    spacing=12,
                    controls=[
                        # Header
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text("⬤", color=BORDER_ON, size=16),
                                ft.Text(
                                    "BRO CHAPERON  AI",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TXT_MAIN,
                                ),
                            ],
                        ),
                        # Zona de Carga
                        self.upload_area,
                        # Sección de Modos de Respuesta
                        ft.Text(
                            "MODO DE RESPUESTA",
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=TXT_SECTION,
                        ),
                        # Fila 1 de Modos (4 modos)
                        ft.Row(
                            spacing=8,
                            controls=[
                                self._build_mode_button(key) for key in MODES_ROW1
                            ],
                        ),
                        # Fila 2 de Modos (2 modos)
                        ft.Row(
                            spacing=8,
                            controls=[
                                self._build_mode_button(key, expand=True)
                                for key in MODES_ROW2
                            ],
                        ),
                        # Área de Respuesta
                        ft.Text(
                            "RESPUESTA GENERADA",
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=TXT_SECTION,
                        ),
                        ft.Container(
                            expand=True,
                            bgcolor=BG_CARD2,
                            border=ft.Border.all(1, BORDER_OFF),
                            border_radius=16,
                            padding=20,
                            content=ft.ListView(
                                expand=True, controls=[self.response_text]
                            ),
                        ),
                        # Botón Copiar
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.ElevatedButton(
                                    content="📋  COPIAR RESPUESTA",
                                    color=BG_ROOT,
                                    bgcolor=WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=25),
                                    ),
                                    height=44,
                                    width=260,
                                    on_click=self._on_copy_click,
                                )
                            ],
                        ),
                        # Footer
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                self.status_text,
                                ft.Text(
                                    "BroChaperonAI · Equipo Alejabot · v2.0",
                                    size=8,
                                    color=TXT_DIM,
                                ),
                            ],
                        ),
                    ],
                ),
                # Columna Derecha (Sidebar)
                ft.Container(
                    expand=3,
                    bgcolor=BG_SIDEBAR,
                    border_radius=16,
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "⚙️  CONFIG",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=BORDER_ON,
                            ),
                            ft.Divider(height=1, color=BORDER_OFF),
                            ft.Text(
                                "RESOLUCIÓN DE VENTANA",
                                size=9,
                                weight=ft.FontWeight.BOLD,
                                color=TXT_SECTION,
                            ),
                            ft.Column(
                                spacing=8,
                                controls=[
                                    self._build_resolution_card(i, label)
                                    for i, (label, _, _) in enumerate(RESOLUTIONS)
                                ],
                            ),
                            ft.Divider(height=16, color=BORDER_OFF),
                            ft.Text(
                                "MODELO IA",
                                size=9,
                                weight=ft.FontWeight.BOLD,
                                color=TXT_SECTION,
                            ),
                            ft.Text(
                                "Nvidia Nemotron VL 12B\nMultimodal Vision (Free)",
                                size=10,
                                color=TXT_MID,
                            ),
                            ft.Divider(height=16, color=BORDER_OFF),
                            ft.Row(
                                controls=[
                                    ft.Text("●", color="#22C55E", size=10),
                                    ft.Text("Sistema listo", size=10, color=TXT_MID),
                                ]
                            ),
                        ]
                    ),
                ),
            ],
        )

        # Envolver todo en un contenedor con padding
        self.page.add(
            ft.Container(
                content=main_layout,
                expand=True,
                padding=16,
            )
        )

        self.page.update()

    def _build_upload_container(self) -> None:
        self.upload_area.content = ft.Container(
            padding=ft.Padding.symmetric(vertical=15, horizontal=20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    self.upload_img_control,
                    self.upload_title_control,
                    self.upload_sub_control,
                    self.progress_bar,
                ],
            ),
        )

    def _build_mode_button(self, key: str, expand: bool = False) -> ft.Container:
        """Crea una tarjeta de modo interactiva con Flet."""
        status = ft.Text("", size=8, color=TXT_DIM)
        self.mode_status_texts[key] = status
        container = ft.Container(
            expand=True,
            bgcolor=BG_CARD,
            border=ft.Border.all(1, BORDER_OFF),
            border_radius=12,
            alignment=ft.alignment.Alignment(0, 0),
            padding=12,
            on_click=lambda _: self._on_mode_click(key),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                controls=[
                    ft.Text(MODE_ICONS[key], size=22),
                    ft.Text(
                        MODE_LABELS[key],
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color=TXT_MID,
                    ),
                    status,
                ],
            ),
        )
        self.mode_containers[key] = container
        return container

    def _build_resolution_card(self, idx: int, label: str) -> ft.Container:
        is_active = idx == self._active_res_idx
        container = ft.Container(
            bgcolor="#1A1030" if is_active else BG_CARD,
            border=ft.Border.all(1, BORDER_ON if is_active else BORDER_OFF),
            border_radius=10,
            padding=10,
            on_click=lambda _: self._on_resolution_click(idx),
            content=ft.Text(
                label,
                size=10,
                weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                color=TXT_MAIN if is_active else TXT_MID,
            ),
        )
        self.res_containers.append(container)
        return container

    def _open_file_dialog(self) -> None:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Selecciona una captura de pantalla",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos", "*.*")],
        )
        root.destroy()
        if path and self.presenter:
            self.presenter.on_load(path)

    def _on_upload_click(self, e) -> None:
        threading.Thread(target=self._open_file_dialog, daemon=True).start()

    def _on_copy_click(self, e) -> None:
        text = self.response_text.value.strip().strip('"')
        if text and text != "":
            safe = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
            self.page.run_js(f"navigator.clipboard.writeText('{safe}')")
            self.set_status("📋 ¡Respuesta copiada al portapapeles!")
            self.page.update()

    def _on_mode_click(self, mode: str) -> None:
        # Limpiar selección anterior
        if self._active_mode and self._active_mode in self.mode_containers:
            self.mode_containers[self._active_mode].border = ft.Border.all(
                1, BORDER_OFF
            )

        # Marcar nuevo activo
        self._active_mode = mode
        self.mode_containers[mode].border = ft.Border.all(1, BORDER_ON)
        self.page.update()

        if self.presenter:
            self.presenter.on_generate(mode)

    def _on_resolution_click(self, idx: int) -> None:
        # Desactivar anterior
        prev_idx = self._active_res_idx
        if prev_idx < len(self.res_containers):
            self.res_containers[prev_idx].bgcolor = BG_CARD
            self.res_containers[prev_idx].border = ft.Border.all(1, BORDER_OFF)
            self.res_containers[prev_idx].content.color = TXT_MID
            self.res_containers[prev_idx].content.weight = ft.FontWeight.NORMAL

        # Activar nueva
        self._active_res_idx = idx
        self.res_containers[idx].bgcolor = "#1A1030"
        self.res_containers[idx].border = ft.Border.all(1, BORDER_ON)
        self.res_containers[idx].content.color = TXT_MAIN
        self.res_containers[idx].content.weight = ft.FontWeight.BOLD

        # Aplicar tamaño de ventana
        _, w, h = RESOLUTIONS[idx]
        self.page.window.width = w
        self.page.window.height = h
        self.page.update()
