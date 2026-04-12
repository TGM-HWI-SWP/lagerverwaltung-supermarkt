"""Services – Business Logic Layer."""

from datetime import datetime
from typing import Dict, List, Optional

from ..domain.product import Product
from ..domain.warehouse import Movement, Warehouse
from ..ports import RepositoryPort


class WarehouseService:
    """Service für Lagerverwaltung.

    Enthält alle Geschäftsvorfälle (Use Cases) für das Lager.
    Kommuniziert ausschließlich über RepositoryPort – nie direkt
    mit einem konkreten Repository (InMemory, JSON, ...).
    """

    def __init__(self, repository: RepositoryPort):
        self.repository = repository
        self.warehouse = Warehouse("Hauptlager")

    # ------------------------------------------------------------------
    # Produkt-Verwaltung
    # ------------------------------------------------------------------

    def create_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str = "",
        initial_quantity: int = 0,
        min_quantity: int = 0,
    ) -> Product:
        """Neues Produkt erstellen und im Repository speichern."""
        if self.repository.load_product(product_id):
            raise ValueError(f"Produkt '{product_id}' existiert bereits.")
        product = Product(
            id=product_id,
            name=name,
            description=description,
            price=price,
            quantity=initial_quantity,
            min_quantity=min_quantity,
            category=category,
        )
        self.repository.save_product(product)
        self.warehouse.add_product(product)
        return product

    def get_product(self, product_id: str) -> Optional[Product]:
        """Ein Produkt anhand seiner ID laden."""
        return self.repository.load_product(product_id)

    def get_all_products(self) -> Dict[str, Product]:
        """Alle Produkte laden."""
        return self.repository.load_all_products()

    def delete_product(self, product_id: str) -> None:
        """Produkt aus dem Repository entfernen."""
        if not self.repository.load_product(product_id):
            raise ValueError(f"Produkt '{product_id}' nicht gefunden.")
        self.repository.delete_product(product_id)

    # ------------------------------------------------------------------
    # Bestandsverwaltung
    # ------------------------------------------------------------------

    def add_to_stock(
        self, product_id: str, quantity: int, reason: str = "", user: str = "system"
    ) -> None:
        """Bestand eines Produkts erhöhen."""
        if quantity <= 0:
            raise ValueError("Menge muss größer 0 sein.")
        product = self._load_or_raise(product_id)
        product.update_quantity(quantity)
        self.repository.save_product(product)
        self._record_movement(product, quantity, "IN", reason, user)

    def remove_from_stock(
        self, product_id: str, quantity: int, reason: str = "", user: str = "system"
    ) -> None:
        """Bestand eines Produkts verringern."""
        if quantity <= 0:
            raise ValueError("Menge muss größer 0 sein.")
        product = self._load_or_raise(product_id)
        if product.quantity < quantity:
            raise ValueError(
                f"Unzureichender Bestand. "
                f"Verfügbar: {product.quantity}, Angefordert: {quantity}"
            )
        product.update_quantity(-quantity)
        self.repository.save_product(product)
        self._record_movement(product, -quantity, "OUT", reason, user)

    # ------------------------------------------------------------------
    # Abfragen für Report A (Businesslogik Rolle 2)
    # ------------------------------------------------------------------

    def get_low_stock_products(self) -> List[Product]:
        """Alle Produkte zurückgeben, deren Bestand unter dem Mindestbestand liegt.

        Ein Produkt ist LOW wenn:
        - min_quantity > 0 ist gesetzt
        - und quantity < min_quantity (aber quantity > 0)
        """
        return [
            p for p in self.repository.load_all_products().values()
            if p.min_quantity > 0 and 0 < p.quantity < p.min_quantity
        ]

    def get_out_of_stock_products(self) -> List[Product]:
        """Alle Produkte zurückgeben, die komplett vergriffen sind (Bestand = 0)."""
        return [
            p for p in self.repository.load_all_products().values()
            if p.quantity <= 0
        ]

    def get_total_inventory_value(self) -> float:
        """Gesamtwert aller Bestände berechnen."""
        return sum(
            p.get_total_value()
            for p in self.repository.load_all_products().values()
        )

    def get_movements(self) -> List[Movement]:
        """Alle Lagerbewegungen laden."""
        return self.repository.load_movements()

    # ------------------------------------------------------------------
    # Interne Hilfsmethoden
    # ------------------------------------------------------------------

    def _load_or_raise(self, product_id: str) -> Product:
        product = self.repository.load_product(product_id)
        if not product:
            raise ValueError(f"Produkt '{product_id}' nicht gefunden.")
        return product

    def _record_movement(
        self,
        product: Product,
        quantity_change: int,
        movement_type: str,
        reason: str,
        user: str,
    ) -> None:
        movement = Movement(
            id=f"mov_{datetime.now().timestamp()}",
            product_id=product.id,
            product_name=product.name,
            quantity_change=quantity_change,
            movement_type=movement_type,
            reason=reason,
            performed_by=user,
        )
        self.repository.save_movement(movement)