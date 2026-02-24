# Changelog – m7nu (Rolle 2)

Dieses Changelog dokumentiert meine Beiträge pro Version (inkl. relevanter Commits).

> Hinweis: Commit-Hashes werden nach dem Push/Merge ergänzt.

## v0.4 – Report A + Kernlogik
- Added Mindestbestand (`min_quantity`) im Domain Model `Product`
- Extended `WarehouseService.create_product()` um `min_quantity`
- Added `InventoryReport` (Report A) als deterministische, testbare Komponente
- Added Unit-Tests für Report A
- Updated `docs/tests.md` und `docs/architecture.md`

Commits:
- TODO