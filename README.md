[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/y3rD5eCg)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22595905&assignment_repo_type=AssignmentRepo)
# Lagerverwaltungssystem - Projektvorlage

Vollständige Projektvorlage für ein professionelles Softwareentwicklungs- und Projektmanagement-Projekt. Dieses Projekt dient als Basis für die Entwicklung einer Lagerverwaltungs- oder Produktverwaltungssoftware mit professionellen Vorgaben.

## Projektüberblick

- **Projektdauer:** 8 Wochen
- **Unterricht:** 2 UE pro Woche
- **Gruppengröße:** 3er- und 4er-Gruppen (Standard: 4er)
- **Ziel:** Professionelle Softwareentwicklung und Projektmanagement

## Installation & Setup

```bash
git clone https://github.com/TGM-HWI-SWP/lagerverwaltung-supermarkt.git#
cd lagerverwaltung-supermarkt

python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Dependencies installieren
pip install -e .
pip install -e ".[dev]"

# 4. Tests ausführen
pytest

# 5. GUI starten
python -m src.ui
```

## Architektur

Das Projekt folgt der **Port-Adapter-Architektur** (auch Hexagonal Architecture genannt):

- **Domain Layer:** Geschäftslogik und Entities (unabhängig von technischen Details)
- **Ports:** Schnittstellen für externe Abhängigkeiten (abstrakt)
- **Adapters:** Konkrete Implementierungen (z.B. In-Memory Repository, Dateisystem, Datenbank)
- **Services:** Geschäftsvorgänge und Use Cases
- **UI:** Benutzeroberfläche

Diese Architektur ermöglicht:
- **Testbarkeit:** Mock-Implementierungen können einfach bereitgestellt werden
- **Austauschbarkeit:** Adapters können leicht ausgetauscht werden
- **Wartbarkeit:** Klare Trennung der Concerns

## Rollenvergabe (4er-Gruppe)

### Rolle 1: Projektverantwortung & Schnittstellen (Contract Owner) -> Elias
- Projektkoordination & Kommunikation
- Zentrale Verantwortung für alle Schnittstellen
- Dokumentation: `docs/contracts.md`
- Release- & Versionsverantwortung
- Unterstützung bei Mergekonflikten

### Rolle 2: Businesslogik & Report A -> Emmanuel
- Implementierung der Kern-Use-Cases
- Umsetzung von Report A (z.B. Lagerstandsreport)
- Zugehörige Tests
- Beispiel: Lagerbewirtschaftung, Bestandsverwaltung

### Rolle 3: Report B & Qualität -> Kerem
- Umsetzung von Report B (z.B. Bewegungsprotokoll, Statistik)
- Erweiterte Tests (Rand- & Fehlerfälle)
- Dummy-Daten erstellen
- Test-Coverage erhöhen

### Rolle 4: GUI & Interaktion -> Philip
- Konzeption & Umsetzung der GUI
- Anbindung an die Businesslogik
- GUI-Tests oder Testbeschreibung

## Testing

### Unit Tests ausführen

```bash
pytest tests/unit/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### Mit Coverage

```bash
pytest --cov=src tests/
```

## Known Issues

Siehe `docs/known_issues.md`

## Lizenz

Schulprojekt - TGM