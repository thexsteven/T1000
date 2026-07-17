# T1000 — Wochenplan bis zum Schreibbeginn

**Autor:** Steven Braun
**Stand:** 17.07.2026
**Deadline:** Schreibbeginn der wissenschaftlichen T1000-Arbeit in spätestens einer Woche
**Prinzip:** Erst Entscheidungen absichern, dann implementieren, dann Ergebnisse produzieren — für die Arbeit zählen begründete Entscheidungen und Ergebniszahlen.

---

## Tag 1–2: Entscheidungen absichern (kritischer Pfad)

### 1. Stage 8 (Cycle Quality Profiling) einmal komplett laufen lassen
- Config anpassen: `stop_after: cycle_quality_profiling`, ggf. `extract_all_cycles: true` oder hohes `max_cycles_to_extract`
- Zuerst starten — Laufzeit vermutlich mehrere Stunden
- **Warum:** Ohne diese Verteilungen bleiben die Ebene-4-Schwellwerte Platzhalter. „Datengetrieben" ist das zentrale Begründungsargument der Arbeit.
- Erwartete Outputs: `signal_quality_metrics.parquet`, `cycle_quality_profile.parquet`, `quality_metric_distribution_summary.csv`

### 2. Gespräch mit der Masterstudentin (anhand `docs/preprocessing_decision_tree.html`)
Zu klären:
- [ ] Herleitung `movement_threshold = 1.0` (Magic Number, 3× dupliziert)
- [ ] Session-Gap 3600 s — ADR-006 sagt „Accepted", Code-Kommentar sagt „exploratory"
- [ ] Velocity-Skalierung (blockiert Variante B der Stillstandsdefinition)
- [ ] Mindest-Session-Größe N (Vorschlag: 100)
- [ ] Zyklusdauer ~3,1 s bestätigt (1,81 s aus früherer Info war falsch/veraltet)

**Warum:** Jede geklärte Frage ist ein begründeter Absatz in der Arbeit.

### 3. Confluence-Dokument finalisieren
- Pipeline-Übersicht (vorhanden) + Entscheidungsbaum + Stillstandsdefinition
- Von Vorgesetzten absegnen lassen — Freigabe **vor** Schreibbeginn einholen

---

## Tag 3–4: Implementieren (Kernbeitrag im Code)

### 4. Pool-Filter-Modul bauen (z. B. `src/preprocessing/pool_selection.py`)
- Input: Zyklustabelle (`cycles.parquet`) + Quality-Metriken (Stage 8)
- Wendet den Entscheidungsbaum an (Ebenen 1–4)
- Output: `pool.parquet` + Ablehnungsprotokoll mit Grund pro Zyklus
- Checks 2.2–2.4 sind trivial (Spalten `duration_seconds`, `number_of_samples`, `minimum_position`, `maximum_position` existieren bereits in cycles.csv)
- Check 2.5 und Ebene 4 brauchen die Stage-8-Outputs aus Schritt 1

### 5. Schwellwerte finalisieren
- Aus den frischen Stage-8-Verteilungen ableiten (Perzentile + Sicherheitsmarge)
- Im Decision-Tree-HTML von „TBD / AWAITING DATA" auf konkrete Werte heben

---

## Tag 5: Ergebnisse produzieren

### 6. Filter über alle 318.252 Zyklen laufen lassen
- Reject-Statistik auswerten: wie viele Zyklen fallen an welcher Station raus und warum
- **Das ist die zentrale Ergebnistabelle/-grafik der T1000** — sie beweist, dass der Baum funktioniert und nötig ist (Beleg: der 8,27-s-Ausreißer fliegt nachweislich raus)

### 7. Schreibmaterial einfrieren
- Zahlen, Tabellen und Plots sichern
- Decision-Tree-HTML (technisch + einfache Version) als Anhang-/Abbildungsmaterial

---

## Bewusst nachrangig

Die **HTML-Visualisierung des Pools** (Zyklen übereinanderlegen) ist laut Aufgabenbeschreibung der Teil *nach* dem Preprocessing. Sie kann parallel zum Schreiben entstehen und blockiert den Schreibbeginn nicht.

---

## Zielbild zum Schreibstart

| Baustein | Status dann |
|---|---|
| Begründete Kriterien (mit Studentin/Vorgesetzten abgestimmt) | ✅ |
| Funktionierender Pool-Filter im Code | ✅ |
| Ergebniszahlen (Reject-Statistik über 318k Zyklen) | ✅ |

Methodik-Kapitel = Entscheidungsbaum, Ergebnis-Kapitel = Reject-Statistik.

---

*Referenzen: `docs/preprocessing_decision_tree.html` (technische Version mit Quellenangaben), `docs/entscheidungsbaum_einfach.html` (einfache Version für Vorgesetzte), Datenbasis `outputs/D63_Nr7_8/Versuch1/20260716_083547/cycles/cycles.csv`*
