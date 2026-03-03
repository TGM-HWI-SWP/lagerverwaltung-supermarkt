"""
LagerPro – DataStore
====================
Singleton für persistente In-Memory-Datenverwaltung via JSON.

Verwendung:
    store = DataStore.instance()
    store.artikel       # Liste aller Artikel
    store.bestellungen  # Liste aller Bestellungen
    store.lieferanten   # Liste aller Lieferanten
    store.save()        # Änderungen speichern
"""

import os
import json


class DataStore:
    _instance = None

    DATA_FILE = os.path.join(os.path.dirname(__file__), "lagerpro_data.json")

    _DEFAULT_DATA = {
        "artikel": [
            {"id": "ABC123", "name": "Bio Vollmilch 1L",   "kategorie": "Molkereiprodukte",  "bestand": 145, "min_bestand": 50,  "preis": 1.29, "lieferant": "Lokaler Bauer",   "mhd": "2025-03-15"},
            {"id": "ASE476", "name": "H-Milch 1L",         "kategorie": "Molkereiprodukte",  "bestand": 320, "min_bestand": 100, "preis": 0.99, "lieferant": "Zentrallager",     "mhd": "2025-06-30"},
            {"id": "NE1789", "name": "H-Milch 0,5L",       "kategorie": "Molkereiprodukte",  "bestand": 12,  "min_bestand": 50,  "preis": 0.79, "lieferant": "Zentrallager",     "mhd": "2025-02-28"},
            {"id": "ABC133", "name": "Bio Orangensaft 1L", "kategorie": "Getränke",          "bestand": 450, "min_bestand": 80,  "preis": 2.49, "lieferant": "Getränke GmbH",    "mhd": "2025-09-01"},
            {"id": "DEF446", "name": "TK Pizza Salami",    "kategorie": "Tiefkühlprodukte",  "bestand": 120, "min_bestand": 30,  "preis": 3.99, "lieferant": "Zentrallager",     "mhd": "2025-12-01"},
            {"id": "CH1799", "name": "Tomaten (1kg)",      "kategorie": "Obst & Gemüse",     "bestand": 20,  "min_bestand": 40,  "preis": 1.99, "lieferant": "Lokale Erzeuger",  "mhd": "2025-02-26"},
        ],
        "bestellungen": [
            {"id": "#567213", "datum": "2025-02-20", "lieferant": "Lokaler Bauer",  "artikel": "Bio Vollmilch 1L",      "menge": 200, "status": "Unterwegs", "gesamt": 258.00},
            {"id": "#567132", "datum": "2025-02-19", "lieferant": "Obst & Gemüse",  "artikel": "Tomaten (1kg)",         "menge": 100, "status": "Unterwegs", "gesamt": 199.00},
            {"id": "#567099", "datum": "2025-02-18", "lieferant": "Pfandflaschen",  "artikel": "Pfandflaschen Palette", "menge": 5,   "status": "Anrufen",   "gesamt": 75.00},
            {"id": "#566988", "datum": "2025-02-17", "lieferant": "Zentrallager",   "artikel": "H-Milch 1L",            "menge": 500, "status": "Geliefert", "gesamt": 495.00},
        ],
        "lieferanten": [
            {"name": "Zentrallager",    "kontakt": "info@zentrallager.de",  "telefon": "089-12345",  "lieferungen": 134},
            {"name": "Lokaler Bauer",   "kontakt": "hof@lokalbauer.de",     "telefon": "08141-9876", "lieferungen": 89},
            {"name": "Getränke GmbH",   "kontakt": "order@getraenke.de",    "telefon": "030-55678",  "lieferungen": 76},
            {"name": "Lokale Erzeuger", "kontakt": "info@lokal.de",         "telefon": "089-44321",  "lieferungen": 121},
        ],
    }

    def __init__(self):
        self._data = self._load()

    @classmethod
    def instance(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Datenzugriff ─────────────────────────────
    @property
    def artikel(self) -> list:
        return self._data["artikel"]

    @property
    def bestellungen(self) -> list:
        return self._data["bestellungen"]

    @property
    def lieferanten(self) -> list:
        return self._data["lieferanten"]

    def lieferanten_namen(self) -> list[str]:
        return [l["name"] for l in self.lieferanten]

    def artikel_namen(self) -> list[str]:
        return [a["name"] for a in self.artikel]

    # ── Index-Suche ───────────────────────────────
    def find_artikel_index(self, artikel_id: str) -> int | None:
        return next((i for i, a in enumerate(self.artikel) if a["id"] == artikel_id), None)

    def find_bestellung_index(self, bestellung_id: str) -> int | None:
        return next((i for i, b in enumerate(self.bestellungen) if b["id"] == bestellung_id), None)

    def find_lieferant_index(self, name: str) -> int | None:
        return next((i for i, l in enumerate(self.lieferanten) if l["name"] == name), None)

    def next_bestellung_id(self) -> str:
        return f"#{len(self.bestellungen) + 1:06d}"

    # ── Persistenz ───────────────────────────────
    def save(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")

    def backup(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def reset(self):
        if os.path.exists(self.DATA_FILE):
            os.remove(self.DATA_FILE)

    def _load(self) -> dict:
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        import copy
        return copy.deepcopy(self._DEFAULT_DATA)
