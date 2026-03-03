"""
LagerPro – Package
==================
Paketstruktur:

  lagerpro/
  ├── __init__.py       – Paket-Einstieg
  ├── colors.py         – AppColors: alle Farbkonstanten
  ├── data_store.py     – DataStore: Singleton Datenverwaltung
  ├── widget_factory.py – WidgetFactory: wiederverwendbare UI-Bausteine
  ├── exporters.py      – CsvExporter, PdfExporter
  ├── music.py          – MusicGenerator, MusicPlayer
  ├── widgets.py        – GradientWidget, LineChart, KpiCard, NavButton, Sidebar, Topbar
  ├── dialogs.py        – Alle Dialog-Fenster
  ├── pages.py          – Alle Seiten (BasePage + konkrete Pages)
  └── main_window.py    – MainWindow
"""

from .main_window import MainWindow

__all__ = ["MainWindow"]
