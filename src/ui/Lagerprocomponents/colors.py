"""
LagerPro – Farbkonstanten
=========================
Zentrale Farbpalette für die gesamte Anwendung.
"""


class AppColors:
    SIDEBAR       = "#0c2145"
    SIDEBAR_DARK  = "#071428"
    SIDEBAR_ACT   = "#1e4080"
    BLUE          = "#1a6bff"
    ORANGE        = "#ff8c00"
    GREEN         = "#28c76f"
    RED           = "#ea5455"
    YELLOW        = "#ff9f43"
    PAGE          = "#eef2f9"
    CARD          = "#ffffff"
    TEXT          = "#1a2a4a"
    MUTED         = "#7b8ea9"
    BORDER        = "#d8e3f0"

    STATUS_COLORS = {
        "Unterwegs":  ("#fff4e0", "#b86200"),
        "Geliefert":  ("#e8faf2", "#1a8a52"),
        "Anrufen":    ("#ffeaea", "#c0392b"),
        "Ausstehend": ("#e8f0ff", "#1a5dcf"),
        "Storniert":  ("#f0f0f0", "#666666"),
    }

    KATEGORIE_ICONS = {
        "Molkereiprodukte": "🥛",
        "Getränke":         "🍹",
        "Obst & Gemüse":    "🥦",
        "Tiefkühlprodukte": "❄",
        "Backwaren":        "🍞",
    }
    KATEGORIE_ICONS_DEFAULT = "📦"

    KATEGORIEN = [
        "Molkereiprodukte", "Getränke", "Obst & Gemüse",
        "Tiefkühlprodukte", "Backwaren", "Sonstiges",
    ]
