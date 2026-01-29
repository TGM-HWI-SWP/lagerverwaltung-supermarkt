# Projektmanagement-Dokumentation

## 1. Projektcharta

### Projektziel
Entwicklung einer Lagerverwaltungssoftware, die:
- grafisch bedienbar ist
- Daten persistent verwaltet
- systematisch getestet wird
- im Team mittels Versionsverwaltung entwickelt wird

### Nicht-Ziele
- Mobile-App-Entwicklung
- Integration mit externer Buchhaltungssoftware (Phase 1)
- Mehrsprachige Benutzeroberfläche
- Hochperformante Verarbeitung von Millionen von Datensätzen

### Stakeholder
| Stakeholder | Interesse | Rolle |
|------------|-----------|-------|
| Lehrperson | Professionelle Ausbildung | Projektbetreuer |
| Schüler/innen (4er-Gruppe) | Praktische Erfahrung | Projektteam |
| Schulleitung | Qualitätsergebnis | Genehmigungsstelle |

### Risiken (Initial)
| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|------------------|--------|-----------|
| Mergekonflikte bei paralleler Arbeit | Hoch | Mittel | Git-Best-Practices, regelmäßige Integrationen |
| Ungleiche Arbeitsverteilung | Mittel | Mittel | Klare Rollenverteilung, Checkpoints |
| Technische Hürden (GUI, Testing) | Mittel | Hoch | Lernmaterial, Pair-Programming |
| Scope-Creep | Mittel | Mittel | Strikte Versioning, Priorisierung |

---

## 2. Vorgehensmodell

### Beschreibung
**Modell:** Iterativ-inkrementelle Entwicklung mit klaren Meilensteinen

**Zyklus pro Woche:**
1. **Montag:** Sprint-Planung, Aufgaben verteilen
2. **Mittwoch:** Checkpoint, Status-Update
3. **Freitag:** Integrieren, Testen, Review

**Wiederholende Praktiken:**
- Daily Standup (kurz)
- Code Reviews vor Merge
- Automatisierte Tests
- Regelmäßige Commits mit aussagekräftigen Meldungen

### Begründung der Wahl
- **Iterativ:** Regelmäßiges Feedback und Anpassung
- **Transparent:** Klare Fortschrittsmessung
- **Praktisch:** Realistisch für 2 UE/Woche
- **Lehrreich:** Schüler/innen lernen echtes Vorgehen

---

## 3. Projektstrukturplan (PSP)

```
Lagerverwaltungssystem (v0.1-v1.0)
│
├── 1. Projektmanagement & Dokumentation
│   ├── 1.1 Projektcharta & PSP
│   ├── 1.2 Rollendefinition
│   ├── 1.3 Risiko-Management
│   └── 1.4 Regelmäßige Rücksprachen
│
├── 2. Softwareentwicklung
│   ├── 2.1 Architektur-Design
│   │   ├── 2.1.1 Port-Adapter-Pattern
│   │   ├── 2.1.2 Service-Layer
│   │   └── 2.1.3 Domain-Modelle
│   ├── 2.2 Domain-Layer (Rolle 2)
│   │   ├── 2.2.1 Product-Klasse
│   │   ├── 2.2.2 Warehouse-Klasse
│   │   └── 2.2.3 Validierung
│   ├── 2.3 Service-Layer (Rolle 2)
│   │   ├── 2.3.1 WarehouseService
│   │   ├── 2.3.2 Geschäftslogik
│   │   └── 2.3.3 Use-Cases
│   ├── 2.4 Persistenz (Alle)
│   │   ├── 2.4.1 Port-Definition
│   │   ├── 2.4.2 In-Memory Adapter
│   │   ├── 2.4.3 SQLite Adapter
│   │   └── 2.4.4 JSON Adapter
│   ├── 2.5 Report A (Rolle 2)
│   │   ├── 2.5.1 Lagerbestandsbericht
│   │   ├── 2.5.2 Report-Logik
│   │   └── 2.5.3 Ausgabe-Format
│   ├── 2.6 Report B (Rolle 3)
│   │   ├── 2.6.1 Bewegungsprotokoll
│   │   ├── 2.6.2 Statistiken
│   │   └── 2.6.3 Grafische Darstellung
│   ├── 2.7 GUI (Rolle 4)
│   │   ├── 2.7.1 Fenster-Design
│   │   ├── 2.7.2 Produktverwaltung
│   │   ├── 2.7.3 Lagerbewegungen
│   │   └── 2.7.4 Reports anzeigen
│   └── 2.8 Testing (Rolle 3)
│       ├── 2.8.1 Unit-Tests
│       ├── 2.8.2 Integration-Tests
│       ├── 2.8.3 GUI-Tests
│       └── 2.8.4 Coverage 90%+
│
├── 3. Dokumentation
│   ├── 3.1 Technische Dokumentation
│   │   ├── 3.1.1 Architecture.md
│   │   ├── 3.1.2 Contracts.md
│   │   ├── 3.1.3 Tests.md
│   │   └── 3.1.4 README.md
│   ├── 3.2 Persönliche Changelogs
│   │   ├── 3.2.1 changelog_rolle1.md
│   │   ├── 3.2.2 changelog_rolle2.md
│   │   ├── 3.2.3 changelog_rolle3.md
│   │   └── 3.2.4 changelog_rolle4.md
│   └── 3.3 Retrospektive
│       └── 3.3.1 Lessons Learned
│
└── 4. Qualitätssicherung & Release
    ├── 4.1 Code-Review
    ├── 4.2 Mergekonflikte lösen
    ├── 4.3 Testen & Bugfixing
    ├── 4.4 Version-Tagging
    └── 4.5 Präsentation & Abschlussbericht
```

---

## 4. Gantt-Diagramm

```
Woche  Aktivität                                    Rolle(n)
=================================================================
1      Projektstart & Rollenverteilung             Alle
       Projektcharta & PSP                         Rolle 1
       Repository-Setup                           Rolle 1
       Basis-Domain-Modelle                       Rolle 2
       
2      Architektur dokumentieren                  Rolle 1
       Ports & Adapters definieren               Rolle 1 + 2
       Service-Layer Skeleton                    Rolle 2
       GUI-Skeleton                              Rolle 4
       Schnittstellen testen                     Rolle 3
       
3      Domain-Layer finalisieren                 Rolle 2
       Repository implementieren                 Rolle 2
       Erste Use-Cases                          Rolle 2
       GUI erweitern                            Rolle 4
       Unit-Tests schreiben                     Rolle 3
       
4      Coding Sprint 1 (Businesslogik)          Rolle 2 + 3
       Report A beginnen                        Rolle 2
       GUI-Integration                          Rolle 4
       Tests erweitern                          Rolle 3
       Dokumentation aktualisieren              Rolle 1
       
5      Coding Sprint 2                          Rolle 2 + 3
       Report A finalisieren                    Rolle 2
       Report B beginnen                        Rolle 3
       GUI-Features                             Rolle 4
       Mergekonflikt-Handling                   Rolle 1
       
6      Report B implementieren                  Rolle 3
       Erweiterte Tests                         Rolle 3
       Dummy-Daten                              Rolle 3
       GUI-Refinement                           Rolle 4
       Code-Review & Stabilisierung             Alle
       
7      Stabilisierung & Bug-Fixes               Alle
       Dokumentation vollständig                Rolle 1
       Coverage 90%+                            Rolle 3
       Performance-Testing                      Rolle 3
       Finale GUI-Polishing                     Rolle 4
       
8      v1.0 Release                             Alle
       Präsentation vorbereiten                 Rolle 1
       Retrospektive durchführen                Alle
       Abschlussbericht schreiben               Alle
       Abgabe                                   Alle

Legende:
======
[████] in Arbeit
[████] abgeschlossen
```

---

## 5. Rollenverteilung

### Rolle 1: Contract Owner & Projektverantwortung
**Hauptaufgaben:**
- Projektkoordination & Kommunikation
- Zentrale Verantwortung für Schnittstellen (docs/contracts.md)
- Release- & Versionsverantwortung
- Mergekonflikte unterstützen
- Dokumentation übersehen

**Abhängigkeiten:**
- Erfordert Input von Rolle 2, 3, 4 für Schnittstellen-Definitionen

**Erfolgskriterien:**
- Alle Contracts aktuell
- Keine unbeantworteten Fragen
- Mergekonflikte dokumentiert

### Rolle 2: Businesslogik & Report A
**Hauptaufgaben:**
- Kern-Use-Cases implementieren
- Report A (Lagerbestandsbericht)
- Domain-Modelle & Validierung
- Service-Layer
- Zugehörige Unit-Tests

**Abhängigkeiten:**
- Braucht Port-Definitionen (von Rolle 1)
- Coordina mit Rolle 3 (Tests), Rolle 4 (GUI-Integration)

**Erfolgskriterien:**
- Alle Use-Cases implementiert
- Report A genau & deterministisch
- 95%+ Test-Coverage für Domain & Service

### Rolle 3: Report B & Qualität
**Hauptaufgaben:**
- Report B (Bewegungsprotokoll, Statistiken)
- Erweiterte Tests (Rand- & Fehlerfälle)
- Dummy-Daten generieren
- Test-Coverage erhöhen
- Performance & Stabilität

**Abhängigkeiten:**
- Braucht stabile Businesslogik (von Rolle 2)
- Coordina mit Rolle 4 (GUI-Tests)

**Erfolgskriterien:**
- Report B aussagekräftig & grafisch
- 90%+ Overall Test-Coverage
- Alle kritischen Fehlerfall-Tests

### Rolle 4: GUI & Interaktion
**Hauptaufgaben:**
- GUI-Design & Umsetzung (PyQt6)
- Anbindung an Businesslogik
- GUI-Tests oder Testbeschreibung
- Benutzerfreundlichkeit
- Responsive Design

**Abhängigkeiten:**
- Braucht stabile Service-API (von Rolle 2)
- Braucht Reports (von Rolle 2, 3)

**Erfolgskriterien:**
- Alle Hauptfunktionen in GUI erreichbar
- Benutzerfreundlich & intuitiv
- Tests oder detaillierte Test-Dokumentation

---

## Wöchentliche Meetings

### Montag (Start)
- Sprint-Planung (30 min)
- Aufgaben verteilen
- Blockers identifizieren

### Mittwoch (Checkpoint)
- Status-Update (15 min)
- Fortschritt besprechen
- Hilfe anfordern

### Freitag (Integration)
- Code-Merge & Review (30 min)
- Tests ausführen
- v0.x Tag erstellen

---

## Erfolgs-Metriken

| Metrik | v0.2 | v0.3 | v0.5 | v1.0 |
|--------|------|------|------|------|
| Commits | 10+ | 20+ | 50+ | 80+ |
| Tests | 5+ | 10+ | 15+ | 20+ |
| Coverage | 70% | 80% | 90% | 95%+ |
| Dokumentation | 50% | 75% | 90% | 100% |
| Mergekonflikte (gelöst) | 1+ | 2+ | 5+ | 10+ |

---

**Projektmanagement-Dokumentation v0.1**  
**Erstellt:** 2025-01-20  
**Aktualisiert von:** [Rolle 1]
