"""
LagerPro – GUI Test
Starte mit: python test_gui.py
"""
import sys, traceback
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

def test(name, fn):
    try:
        fn()
        print(f"✅ {name}")
    except Exception:
        print(f"❌ {name}")
        traceback.print_exc()

# Imports
test("Import main_window",  lambda: __import__("src.ui.main_window", fromlist=["MainWindow"]))
test("Import widgets",      lambda: __import__("src.ui.widgets",     fromlist=["Sidebar", "Topbar"]))
test("Import pages",        lambda: __import__("src.ui.pages",       fromlist=["*"]))
test("Import music",        lambda: __import__("src.ui.music",       fromlist=["MusicPlayer"]))

# Pages
from src.ui import pages
from src.ui.music import MusicPlayer
mp = MusicPlayer()

for cls_name in ["DashboardPage","LagerbestandPage","BestellungenPage","ArtikelverwaltungPage",
                 "BestaetigungPage","ArtikellistePage","LieferantenPage","BerichtePage"]:
    test(f"Instanz {cls_name}", lambda c=cls_name: getattr(pages, c)())

test("Instanz EinstellungenPage", lambda: pages.EinstellungenPage(music_player=mp))

# Widgets & MainWindow
from src.ui.widgets import Sidebar, Topbar
from src.ui.main_window import MainWindow

test("Topbar",      lambda: Topbar())
test("Sidebar",     lambda: Sidebar(lambda i, n: None, music_player=mp))
test("MainWindow",  lambda: MainWindow())

def t_show():
    win = MainWindow()
    win.show()
    app.processEvents()
    assert win.isVisible(), "Fenster nicht sichtbar!"
    win.close()

test("MainWindow sichtbar", t_show)