"""
LagerPro – Musik
================
MusicGenerator : Programmatische Lo-Fi WAV-Erzeugung
MusicPlayer    : Kompakter Musik-Player-Widget für die Sidebar
"""

import math
import os
import struct
import tempfile
import wave

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# pygame optional
MUSIC_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init()
    MUSIC_AVAILABLE = True
except Exception:
    pass


class MusicGenerator:
    """Generiert einen Lo-Fi Ambient WAV-Track vollständig im Speicher."""

    CHORDS = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 415.30],  # Am7
        [174.61, 220.00, 261.63, 349.23],  # Fmaj7
        [196.00, 246.94, 293.66, 392.00],  # G7
    ]

    @classmethod
    def generate(cls, path: str, duration: int = 30, sample_rate: int = 44100):
        import random
        random.seed(42)
        n = sample_rate * duration
        chord_len = sample_rate * (duration // len(cls.CHORDS))
        samples = []

        for i in range(n):
            t = i / sample_rate
            chord_idx = min(i // chord_len, len(cls.CHORDS) - 1)
            freqs = cls.CHORDS[chord_idx]

            val = sum(
                math.sin(2 * math.pi * f * (1.0 + random.uniform(-0.002, 0.002)) * t) * 0.12
                for f in freqs
            )
            val += math.sin(2 * math.pi * (freqs[0] / 2) * t) * 0.10
            val += random.uniform(-0.015, 0.015)

            pos_in_chord = (i % chord_len) / chord_len
            val *= math.sin(math.pi * pos_in_chord) ** 0.5 * 0.6
            val = max(-1.0, min(1.0, val))
            samples.append(int(val * 32767))

        with wave.open(path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))


class MusicPlayer(QWidget):
    """Kompakter Musik-Player-Widget am unteren Ende der Sidebar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("background: transparent;")
        self._playing = False
        self._volume = 0.5
        self._music_path = None
        self._build_ui()
        if MUSIC_AVAILABLE:
            self._prepare_music()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 4, 10, 4)
        lay.setSpacing(2)

        # Titelzeile
        title_row = QHBoxLayout()
        self._track_label = QLabel("🎵 Lo-Fi Ambient")
        self._track_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._track_label.setStyleSheet("color: rgba(255,255,255,180); background: transparent;")
        title_row.addWidget(self._track_label)
        title_row.addStretch()
        lay.addLayout(title_row)

        # Steuerungszeile
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(6)

        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(30, 30)
        self._play_btn.setFont(QFont("Segoe UI", 12))
        self._play_btn.setCursor(Qt.PointingHandCursor)
        self._play_btn.setStyleSheet("""
            QPushButton { background: #1a6bff; color: white; border-radius: 15px; border: none; }
            QPushButton:hover { background: #0d4fcf; }
        """)
        self._play_btn.clicked.connect(self._toggle_play)

        btn_style = ("QPushButton { background:transparent; border:none; "
                     "color:rgba(255,255,255,160); font-size:13px; } "
                     "QPushButton:hover { color:white; }")
        vol_down = QPushButton("🔉")
        vol_down.setFixedSize(26, 26)
        vol_down.setStyleSheet(btn_style)
        vol_down.clicked.connect(lambda: self._set_volume(max(0.0, self._volume - 0.15)))

        vol_up = QPushButton("🔊")
        vol_up.setFixedSize(26, 26)
        vol_up.setStyleSheet(btn_style)
        vol_up.clicked.connect(lambda: self._set_volume(min(1.0, self._volume + 0.15)))

        self._vol_label = QLabel(f"{int(self._volume * 100)}%")
        self._vol_label.setFont(QFont("Segoe UI", 9))
        self._vol_label.setStyleSheet("color: rgba(255,255,255,120); background: transparent;")
        self._vol_label.setFixedWidth(34)

        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont("Segoe UI", 10))
        self._status_dot.setStyleSheet("color: #555; background: transparent;")

        ctrl_row.addWidget(self._play_btn)
        ctrl_row.addWidget(vol_down)
        ctrl_row.addWidget(self._vol_label)
        ctrl_row.addWidget(vol_up)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self._status_dot)
        lay.addLayout(ctrl_row)

    def _prepare_music(self):
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            self._music_path = tmp.name
            MusicGenerator.generate(self._music_path, duration=30)
        except Exception as e:
            print(f"Music gen error: {e}")

    def _toggle_play(self):
        if not MUSIC_AVAILABLE:
            QMessageBox.information(self, "Musik", "Installiere pygame:\n\npip install pygame")
            return
        self._stop() if self._playing else self._play()

    def _play(self):
        if not self._music_path or not os.path.exists(self._music_path):
            return
        try:
            pygame.mixer.music.load(self._music_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play(-1)
            self._playing = True
            self._play_btn.setText("⏸")
            self._status_dot.setStyleSheet("color: #28c76f; background: transparent;")
            self._track_label.setText("🎵 Lo-Fi Ambient  ♪")
        except Exception as e:
            print(f"Music play error: {e}")

    def _stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._playing = False
        self._play_btn.setText("▶")
        self._status_dot.setStyleSheet("color: #555; background: transparent;")
        self._track_label.setText("🎵 Lo-Fi Ambient")

    def _set_volume(self, volume: float):
        self._volume = volume
        self._vol_label.setText(f"{int(volume * 100)}%")
        if MUSIC_AVAILABLE and self._playing:
            try:
                pygame.mixer.music.set_volume(volume)
            except Exception:
                pass

    def closeEvent(self, event):
        self._stop()
        if self._music_path and os.path.exists(self._music_path):
            try:
                os.unlink(self._music_path)
            except Exception:
                pass
        super().closeEvent(event)