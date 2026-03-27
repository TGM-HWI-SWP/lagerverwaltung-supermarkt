"""
LagerPro Software – Einstiegspunkt
====================================
Starte die Anwendung mit:
    python lagerpro_app.py

Installation:
    pip install PyQt5 reportlab pygame
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from .main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 12))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()