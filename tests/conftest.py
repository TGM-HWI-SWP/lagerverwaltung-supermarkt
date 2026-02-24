"""Pytest Configuration"""

import sys
from pathlib import Path

# Pfad zur Projektwurzel hinzufügen, damit `import src...` funktioniert
sys.path.insert(0, str(Path(__file__).parent.parent))