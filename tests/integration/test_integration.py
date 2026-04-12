"""Integration Tests – testet das Zusammenspiel aller Schichten.

Testet:
- Kompletter Workflow mit InMemoryRepository
- Kompletter Workflow mit JsonFileRepository (zweites Backend!)
- Report A generate() + render() im Zusammenspiel
- ConsoleReportAdapter (nutzt InventoryReport intern)
- Service-Methoden get_low_stock / get_out_of_stock
"""

import os
import tempfile

import pytest
from src.adapters.report import ConsoleReportAdapter
from src.adapters.repository import InMemoryRepository, JsonFileRepository, RepositoryFactory
from src.reports import InventoryReport
from src.services import WarehouseService


# ---------------------------------------------------------------------------
# 1. Workflow mit InMemoryRepository
# ---------------------------------------------------------------------------

class TestIntegrationInMemory:

    def test_full_workflow_in_memory(self):
        repo = RepositoryFactory.create_repository("memory")
        service = WarehouseService(repo)

        service.create_product("LAPTOP-001", "Laptop ProBook", "Hochwertiger Laptop",
                               1200.0, category="Elektronik", initial_quantity=5)
        service.create_product("MOUSE-001", "Wireless Mouse", "Ergonomische Maus",
                               25.0, category="Zubehör", initial_quantity=50)

        service.add_to_stock("LAPTOP-001", 3, reason="Bestellung #123", user="Max")
        service.remove_from_stock("LAPTOP-001", 2, reason="Verkauf", user="Anna")
        service.add_to_stock("MOUSE-001", 10, reason="Nachbestellung", user="Max")

        laptop = service.get_product("LAPTOP-001")
        assert laptop.quantity == 6  # 5 + 3 - 2

        movements = service.get_movements()
        assert len(movements) == 3

        total = service.get_total_inventory_value()
        assert total == pytest.approx(1200 * 6 + 25 * 60)

    def test_low_and_out_stock_queries(self):
        repo = InMemoryRepository()
        service = WarehouseService(repo)

        service.create_product("P001", "OK", "", 1.0, initial_quantity=10, min_quantity=5)
        service.create_product("P002", "LOW", "", 1.0, initial_quantity=2, min_quantity=5)
        service.create_product("P003", "OUT", "", 1.0, initial_quantity=0, min_quantity=1)

        low = service.get_low_stock_products()
        out = service.get_out_of_stock_products()

        assert len(low) == 1
        assert low[0].id == "P002"
        assert len(out) == 1
        assert out[0].id == "P003"


# ---------------------------------------------------------------------------
# 2. Workflow mit JsonFileRepository (zweites Backend)
# ---------------------------------------------------------------------------

class TestIntegrationJsonBackend:
    """Testet JsonFileRepository – persistentes Backend."""

    def test_json_backend_speichert_und_laedt(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            repo = JsonFileRepository(filepath=path)
            service = WarehouseService(repo)

            service.create_product("J001", "JSON-Produkt", "Test", 9.99,
                                   initial_quantity=5, min_quantity=2)
            service.add_to_stock("J001", 3, reason="Nachfüllen")

            # Neues Repository-Objekt auf dieselbe Datei → Daten müssen noch da sein
            repo2 = JsonFileRepository(filepath=path)
            product = repo2.load_product("J001")
            assert product is not None
            assert product.name == "JSON-Produkt"
            assert product.quantity == 8  # 5 + 3

        finally:
            os.unlink(path)

    def test_json_backend_movements_persistent(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            repo = JsonFileRepository(filepath=path)
            service = WarehouseService(repo)
            service.create_product("J001", "Test", "", 1.0, initial_quantity=10)
            service.add_to_stock("J001", 5)
            service.remove_from_stock("J001", 2)

            repo2 = JsonFileRepository(filepath=path)
            movements = repo2.load_movements()
            assert len(movements) == 2

        finally:
            os.unlink(path)

    def test_factory_erstellt_json_repo(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            repo = RepositoryFactory.create_repository("json", filepath=path)
            assert isinstance(repo, JsonFileRepository)
        finally:
            os.unlink(path)

    def test_factory_unbekannter_typ_wirft_fehler(self):
        with pytest.raises(ValueError):
            RepositoryFactory.create_repository("sqlite")


# ---------------------------------------------------------------------------
# 3. Report A im Zusammenspiel (generate + render)
# ---------------------------------------------------------------------------

class TestIntegrationReportA:

    def test_report_a_generate_und_render(self):
        repo = InMemoryRepository()
        service = WarehouseService(repo)

        service.create_product("P001", "Produkt A", "Test", 100.0, initial_quantity=10)
        service.create_product("P002", "Produkt B", "Test", 50.0,
                               initial_quantity=2, min_quantity=5)

        report = InventoryReport(repo)
        result = report.generate()
        text = report.render(result)

        assert result.product_count == 2
        assert result.low_stock_count == 1
        assert "LAGERSTANDSREPORT" in text
        assert "P001" in text
        assert "P002" in text
        assert "LOW" in text


# ---------------------------------------------------------------------------
# 4. ConsoleReportAdapter nutzt InventoryReport
# ---------------------------------------------------------------------------

class TestIntegrationConsoleAdapter:

    def test_adapter_inventory_report(self):
        repo = InMemoryRepository()
        service = WarehouseService(repo)
        service.create_product("P001", "Produkt A", "Test", 100.0, initial_quantity=10)

        adapter = ConsoleReportAdapter(repo)
        text = adapter.generate_inventory_report()

        assert "LAGERSTANDSREPORT" in text
        assert "P001" in text

    def test_adapter_movement_report(self):
        repo = InMemoryRepository()
        service = WarehouseService(repo)
        service.create_product("P001", "Test", "", 10.0, initial_quantity=5)
        service.add_to_stock("P001", 3)
        service.remove_from_stock("P001", 1)

        adapter = ConsoleReportAdapter(repo)
        text = adapter.generate_movement_report()

        assert "BEWEGUNGSPROTOKOLL" in text
        assert "P001" in text

    def test_adapter_leeres_lager(self):
        repo = InMemoryRepository()
        adapter = ConsoleReportAdapter(repo)
        inv = adapter.generate_inventory_report()
        mov = adapter.generate_movement_report()
        assert len(inv) > 0
        assert len(mov) > 0