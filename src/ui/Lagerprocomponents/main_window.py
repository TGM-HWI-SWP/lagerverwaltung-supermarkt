"""
LagerPro – Hauptfenster
========================
MainWindow verbindet Sidebar, Topbar und alle Seiten im QStackedWidget.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont

from .music import MusicPlayer, MUSIC_AVAILABLE
from .widgets import Sidebar, Topbar
from .pages import (
    DashboardPage, LagerbestandPage, BestellungenPage, ArtikelverwaltungPage,
    BestaetigungPage, ArtikellistePage, LieferantenPage, BerichtePage, EinstellungenPage,
)


class MainWindow(QMainWindow):
    """Hauptfenster: enthält Sidebar, Topbar und alle Seiten im StackedWidget."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LagerPro Software")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        # Musik-Player zuerst erstellen (wird von Sidebar und EinstellungenPage gebraucht)
        self._music_player = MusicPlayer()

        # Alle Seiten anlegen
        self._pages = [
            DashboardPage(),
            LagerbestandPage(),
            BestellungenPage(),
            ArtikelverwaltungPage(),
            BestaetigungPage(),
            ArtikellistePage(),
            LieferantenPage(),
            BerichtePage(),
            EinstellungenPage(music_player=self._music_player),
        ]

        # Stack mit allen Seiten befüllen
        self._stack = QStackedWidget()
        for page in self._pages:
            self._stack.addWidget(page)

        # Sidebar mit Navigation und Musik-Player
        self._sidebar = Sidebar(self._navigate, music_player=self._music_player)

        # Layout zusammenbauen
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)
        right_lay.addWidget(Topbar())
        right_lay.addWidget(self._stack)

        main_lay.addWidget(self._sidebar)
        main_lay.addWidget(right)

    def _navigate(self, idx: int, name: str):
        self._stack.setCurrentIndex(idx)

    def closeEvent(self, event):
        if MUSIC_AVAILABLE:
            try:
                self._music_player._stop()
            except Exception:
                pass
        super().closeEvent(event)
