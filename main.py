from src.adapters.repository import InMemoryRepository
from src.services import WarehouseService
from src.reports import InventoryReport

# Repository und Service erstellen
repo = InMemoryRepository()
service = WarehouseService(repo)

# Testdaten anlegen
service.create_product("MILCH-01", "Vollmilch", "1L", 1.50,
                       category="Molkerei", initial_quantity=10, min_quantity=5)
service.create_product("BROT-01", "Brot", "500g", 2.00,
                       category="Backwaren", initial_quantity=2, min_quantity=5)
service.create_product("EIER-01", "Eier", "10er", 3.00,
                       category="Frische", initial_quantity=0, min_quantity=4)

# Report erstellen
report = InventoryReport(repo)
result = report.generate()

# Text ausgeben (Konsole)
print(report.render_text(result))

# HTML speichern → im Browser öffnen → Drucken → Als PDF
report.save_html(result, "report.html")