"""Repository Adapter – In-Memory und JSON-File-Implementierungen.

Zwei Backends stehen zur Verfügung:
- InMemoryRepository : schnell, flüchtig – ideal für Tests
- JsonFileRepository : persistiert Daten in einer JSON-Datei
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement
from ..ports import RepositoryPort


# ---------------------------------------------------------------------------
# Backend 1: In-Memory (für Tests und schnelle Prototypen)
# ---------------------------------------------------------------------------

class InMemoryRepository(RepositoryPort):
    """In-Memory Repository – schnell für Tests und schnelle Prototypen."""

    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._movements: List[Movement] = []

    def save_product(self, product: Product) -> None:
        self._products[product.id] = product

    def load_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    def load_all_products(self) -> Dict[str, Product]:
        return self._products.copy()

    def delete_product(self, product_id: str) -> None:
        self._products.pop(product_id, None)

    def save_movement(self, movement: Movement) -> None:
        self._movements.append(movement)

    def load_movements(self) -> List[Movement]:
        return self._movements.copy()


# ---------------------------------------------------------------------------
# Backend 2: JSON-File (persistiert Daten auf der Festplatte)
# ---------------------------------------------------------------------------

class JsonFileRepository(RepositoryPort):
    """JSON-File Repository – speichert Daten persistent in einer JSON-Datei.

    Warum ein zweites Backend?
    - InMemoryRepository verliert alle Daten beim Programmende.
    - JsonFileRepository schreibt alles in eine .json-Datei,
      sodass die Daten auch nach einem Neustart noch vorhanden sind.
    - Beide implementieren dasselbe RepositoryPort-Interface,
      sodass der restliche Code (Services, Reports) sich nicht ändert.
    """

    def __init__(self, filepath: str = "data/warehouse.json"):
        self._filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            self._write({"products": {}, "movements": []})

    # --- Hilfsmethoden für JSON-Serialisierung ---

    def _read(self) -> dict:
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def _product_to_dict(product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "min_quantity": product.min_quantity,
            "sku": product.sku,
            "category": product.category,
            "notes": product.notes,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_product(d: dict) -> Product:
        return Product(
            id=d["id"],
            name=d["name"],
            description=d["description"],
            price=d["price"],
            quantity=d["quantity"],
            min_quantity=d.get("min_quantity", 0),
            sku=d.get("sku", ""),
            category=d.get("category", ""),
            notes=d.get("notes"),
        )

    @staticmethod
    def _movement_to_dict(m: Movement) -> dict:
        return {
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product_name,
            "quantity_change": m.quantity_change,
            "movement_type": m.movement_type,
            "reason": m.reason,
            "performed_by": m.performed_by,
            "timestamp": m.timestamp.isoformat(),
        }

    @staticmethod
    def _dict_to_movement(d: dict) -> Movement:
        return Movement(
            id=d["id"],
            product_id=d["product_id"],
            product_name=d["product_name"],
            quantity_change=d["quantity_change"],
            movement_type=d["movement_type"],
            reason=d.get("reason"),
            performed_by=d.get("performed_by", "system"),
            timestamp=datetime.fromisoformat(d["timestamp"]),
        )

    # --- RepositoryPort Implementierung ---

    def save_product(self, product: Product) -> None:
        data = self._read()
        data["products"][product.id] = self._product_to_dict(product)
        self._write(data)

    def load_product(self, product_id: str) -> Optional[Product]:
        data = self._read()
        raw = data["products"].get(product_id)
        return self._dict_to_product(raw) if raw else None

    def load_all_products(self) -> Dict[str, Product]:
        data = self._read()
        return {
            pid: self._dict_to_product(d)
            for pid, d in data["products"].items()
        }

    def delete_product(self, product_id: str) -> None:
        data = self._read()
        data["products"].pop(product_id, None)
        self._write(data)

    def save_movement(self, movement: Movement) -> None:
        data = self._read()
        data["movements"].append(self._movement_to_dict(movement))
        self._write(data)

    def load_movements(self) -> List[Movement]:
        data = self._read()
        return [self._dict_to_movement(d) for d in data["movements"]]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class RepositoryFactory:
    """Factory für Repository-Instanzen.

    Ermöglicht einfaches Umschalten zwischen den Backends
    ohne den restlichen Code zu ändern (Port-Adapter-Pattern).
    """

    @staticmethod
    def create_repository(repository_type: str = "memory", **kwargs) -> RepositoryPort:
        """Repository basierend auf Typ erstellen.

        Args:
            repository_type: "memory" oder "json"
            **kwargs: z.B. filepath="data/mein_lager.json" für JsonFileRepository

        Returns:
            RepositoryPort-Instanz
        """
        if repository_type == "memory":
            return InMemoryRepository()
        elif repository_type == "json":
            filepath = kwargs.get("filepath", "data/warehouse.json")
            return JsonFileRepository(filepath=filepath)
        else:
            raise ValueError(
                f"Unbekannter Repository-Typ: '{repository_type}'. "
                f"Erlaubt: 'memory', 'json'"
            )