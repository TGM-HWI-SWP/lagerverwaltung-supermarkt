"""Unit Tests für Report A (InventoryReport).

Testet:
- Leeres Repository
- Status-Berechnung (OK / LOW / OUT)
- Gesamtwert-Berechnung
- Deterministische Sortierung
- render()-Ausgabe
- Produkte ohne Mindestbestand (min_quantity=0)
- Randfälle (Preis=0, einzelnes Produkt, ...)
"""

import pytest
from src.adapters.repository import InMemoryRepository
from src.reports import InventoryReport, InventoryReportResult
from src.services import WarehouseService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo():
    return InMemoryRepository()


@pytest.fixture
def service(repo):
    return WarehouseService(repo)


# ---------------------------------------------------------------------------
# 1. Leeres Repository
# ---------------------------------------------------------------------------

class TestInventoryReportEmpty:

    def test_empty_repo_gives_zero_counts(self, repo):
        result = InventoryReport(repo).generate()
        assert result.product_count == 0
        assert result.total_inventory_value == 0.0
        assert result.low_stock_count == 0
        assert result.out_of_stock_count == 0
        assert result.ok_count == 0
        assert result.rows == []

    def test_render_empty_repo(self, repo):
        result = InventoryReport(repo).generate()
        text = InventoryReport(repo).render(result)
        assert isinstance(text, str)
        assert len(text) > 0


# ---------------------------------------------------------------------------
# 2. Status-Logik (OK / LOW / OUT)
# ---------------------------------------------------------------------------

class TestInventoryReportStatus:

    def test_status_ok_wenn_bestand_ausreichend(self, repo, service):
        service.create_product("P001", "Milch", "1L", 1.50,
                               initial_quantity=10, min_quantity=5)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "OK"
        assert result.ok_count == 1
        assert result.low_stock_count == 0
        assert result.out_of_stock_count == 0

    def test_status_low_wenn_unter_mindestbestand(self, repo, service):
        service.create_product("P001", "Brot", "Vollkorn", 2.00,
                               initial_quantity=2, min_quantity=5)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "LOW"
        assert result.low_stock_count == 1
        assert result.ok_count == 0

    def test_status_out_wenn_bestand_null(self, repo, service):
        service.create_product("P001", "Eier", "10er", 3.00,
                               initial_quantity=0, min_quantity=4)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "OUT"
        assert result.out_of_stock_count == 1

    def test_kein_low_wenn_min_quantity_null(self, repo, service):
        """Wenn kein Mindestbestand gesetzt, kann ein Produkt nie LOW sein."""
        service.create_product("P001", "Zucker", "1kg", 1.00,
                               initial_quantity=1, min_quantity=0)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "OK"
        assert result.low_stock_count == 0

    def test_out_hat_vorrang_vor_low(self, repo, service):
        """Bestand=0 ist immer OUT, auch wenn min_quantity gesetzt ist."""
        service.create_product("P001", "Salz", "500g", 0.80,
                               initial_quantity=0, min_quantity=3)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "OUT"

    def test_genau_mindestbestand_ist_ok(self, repo, service):
        """quantity == min_quantity → OK (nicht LOW)."""
        service.create_product("P001", "Öl", "1L", 2.50,
                               initial_quantity=5, min_quantity=5)
        result = InventoryReport(repo).generate()
        assert result.rows[0].status == "OK"


# ---------------------------------------------------------------------------
# 3. Gesamtwert und Kennzahlen
# ---------------------------------------------------------------------------

class TestInventoryReportTotals:

    def test_gesamtwert_korrekt(self, repo, service):
        service.create_product("P001", "A", "", 10.00, initial_quantity=3)
        service.create_product("P002", "B", "", 5.00, initial_quantity=4)
        result = InventoryReport(repo).generate()
        assert result.total_inventory_value == pytest.approx(10*3 + 5*4)

    def test_produkt_count_korrekt(self, repo, service):
        service.create_product("P001", "A", "", 1.0, initial_quantity=1)
        service.create_product("P002", "B", "", 1.0, initial_quantity=1)
        service.create_product("P003", "C", "", 1.0, initial_quantity=1)
        result = InventoryReport(repo).generate()
        assert result.product_count == 3

    def test_alle_status_zaehler_zusammen(self, repo, service):
        service.create_product("P001", "OK-Prod", "", 1.0,
                               initial_quantity=10, min_quantity=5)   # OK
        service.create_product("P002", "Low-Prod", "", 2.0,
                               initial_quantity=2, min_quantity=5)    # LOW
        service.create_product("P003", "Out-Prod", "", 3.0,
                               initial_quantity=0, min_quantity=1)    # OUT
        result = InventoryReport(repo).generate()
        assert result.ok_count == 1
        assert result.low_stock_count == 1
        assert result.out_of_stock_count == 1
        assert result.product_count == 3


# ---------------------------------------------------------------------------
# 4. Deterministische Sortierung
# ---------------------------------------------------------------------------

class TestInventoryReportSorting:

    def test_reihenfolge_alphabetisch_nach_id(self, repo, service):
        service.create_product("P003", "C", "", 1.0)
        service.create_product("P001", "A", "", 1.0)
        service.create_product("P002", "B", "", 1.0)
        result = InventoryReport(repo).generate()
        ids = [r.product_id for r in result.rows]
        assert ids == ["P001", "P002", "P003"]

    def test_gleiche_daten_gleiche_reihenfolge(self, repo, service):
        """Zwei aufeinanderfolgende generate()-Aufrufe müssen identisch sein."""
        service.create_product("B001", "Brot", "", 2.0, initial_quantity=5)
        service.create_product("A001", "Apfel", "", 0.5, initial_quantity=20)
        r1 = InventoryReport(repo).generate()
        r2 = InventoryReport(repo).generate()
        assert [r.product_id for r in r1.rows] == [r.product_id for r in r2.rows]


# ---------------------------------------------------------------------------
# 5. render()-Methode
# ---------------------------------------------------------------------------

class TestInventoryReportRender:

    def test_render_enthaelt_product_id(self, repo, service):
        service.create_product("MILK-01", "Vollmilch", "1L", 1.29, initial_quantity=10)
        report = InventoryReport(repo)
        result = report.generate()
        text = report.render(result)
        assert "MILK-01" in text

    def test_render_enthaelt_status_symbole(self, repo, service):
        service.create_product("P001", "A", "", 1.0,
                               initial_quantity=0, min_quantity=1)  # OUT
        report = InventoryReport(repo)
        text = report.render(report.generate())
        assert "OUT" in text

    def test_render_enthaelt_gesamtwert(self, repo, service):
        service.create_product("P001", "A", "", 5.00, initial_quantity=4)
        report = InventoryReport(repo)
        result = report.generate()
        text = report.render(result)
        assert "20.00" in text  # 5 * 4 = 20

    def test_render_gibt_string_zurueck(self, repo, service):
        service.create_product("P001", "A", "", 1.0, initial_quantity=1)
        report = InventoryReport(repo)
        text = report.render(report.generate())
        assert isinstance(text, str)
        assert len(text) > 50  # kein leerer Output

    def test_render_enthaelt_header(self, repo, service):
        report = InventoryReport(repo)
        text = report.render(report.generate())
        assert "LAGERSTANDSREPORT" in text


# ---------------------------------------------------------------------------
# 6. Row-Daten korrekt
# ---------------------------------------------------------------------------

class TestInventoryReportRow:

    def test_row_felder_korrekt(self, repo, service):
        service.create_product("P001", "Milch", "1L", 1.50,
                               category="Molkerei",
                               initial_quantity=10,
                               min_quantity=5)
        result = InventoryReport(repo).generate()
        row = result.rows[0]
        assert row.product_id == "P001"
        assert row.name == "Milch"
        assert row.category == "Molkerei"
        assert row.quantity == 10
        assert row.min_quantity == 5
        assert row.price == pytest.approx(1.50)
        assert row.total_value == pytest.approx(15.00)
        assert row.status == "OK"