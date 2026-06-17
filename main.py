# =============================================================================
# main.py — Punto de entrada de RossaliniChat en Flet
# =============================================================================

from dotenv import load_dotenv

load_dotenv()  # Carga .env antes de instanciar AIEngine

import flet as ft
from app.views.main_window import MainWindow
from app.presenters.chat_presenter import ChatPresenter


def main() -> None:
    """Arranca la aplicación Flet con la vista MainWindow."""

    def main_flet(page: ft.Page) -> None:
        view = MainWindow(page)
        presenter = ChatPresenter(view)
        view.set_presenter(presenter)
        view.build_ui()

    ft.run(main_flet)


if __name__ == "__main__":
    main()
