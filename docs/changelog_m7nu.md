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
- bb6aef2 changelog geupdated
- 7647711 Rolle 4, ProductDialogWindow für später erwähnt
- 6ac5632 changelog dateiname geändert auf github namen
- c8d24bb product.py min_quantity update
- 642bb7c changelog + min_quantity + report A ergänzt
- 481148e abschnitt Report A ergänzt
- f224bca fix richtiger erwarteter warenwert
- ddee41b Unit-Tests für Report A
- b96f1a0 fix damit import src... funktioniert
- 4a90f2b reports init py
- 6f307a3 report A als eigene, testbare komponente
- c1d2fb1 use-cases + validierung + min_quantity
- 8be3365 mindestbestand min_quantity