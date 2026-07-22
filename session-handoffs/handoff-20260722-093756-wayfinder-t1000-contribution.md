# Handoff: Wayfinder map — t1000 as a defended, additive contribution

Date: 2026-07-22
Workspace: `/home/ita/t1000`
Skill: `/wayfinder` (charting + first working pass)

## Was passiert ist

Auf die lose Idee des Users hin — *"sicherstellen, dass t1000 dem
Master-Thesis-Projekt echten, additiven Mehrwert bringt"* — wurde eine
**Wayfinder-Map** angelegt und die erste Runde bearbeitet.

- **Tracker:** local-markdown (Default), da keine `docs/agents/issue-tracker.md`
  konfiguriert ist. Map + Tickets liegen unter
  `.scratch/t1000-contribution/` (`map.md` + `issues/NN-*.md`).
- **Destination:** ein *gesperrter, verteidigbarer Plan* (Hand-off-Spec, kein
  gebauter Code) für t1000 als **physical-plausibility Pre-Stage integriert in
  Fatemehs Pipeline**, der die Glaubwürdigkeitslücken schließt — belastbar
  gegenüber (1) DHBW-Prüfern, (2) Fatemeh/Thesis, (3) Emerson-Ingenieuren.
- **Grundsatzentscheidung beim Charting:** Integration (Pre-Stage), nicht
  Standalone-Layer.

## Entscheidungen (Decisions so far — im Detail in den Tickets)

- **02 Attach point (resolved, research):** Seam liegt zwischen Stage 5
  `cycle_detection` und Stage 6 `multi_sensor_extraction`. Objekt = per-cycle
  `cycles.parquet`-Index (nur Position-Features, Key `cycle_id`). Keine
  Rejection-Flag dort → Hand-off als gefilterter Pool oder annotierte Tabelle.
  `cycle_selection.py` ist der dokumentierte opt-in-Präzedenzfall. Drei
  Seam-Optionen (A gefilterter Index / B neue Stage / C annotierte Tabelle).
- **01 Threshold-Evidence (resolved, research):** Alle drei Schwellen provisorisch.
  session-gap 3600 s und movement >1.0 sind aus vorhandenen
  `outputs/D63_Nr7_8/…`-Artefakten billig re-derivierbar; velocity scaling ist
  auf eine Einheiten/Spec-Frage blockiert (deklariert `m/s`, Werte physikalisch
  unmöglich).
- **03 Justification strategy (resolved, grilling) — Kern dieser Session:**
  **Ein empirischer Pillar** (eine Position-Signal-Studie, ~3 Tage) re-deriviert
  BEIDE Position-Schwellen (session-gap aus Timestamp-Gap-Verteilung, movement
  >1.0 aus Min-Position-Noise-Floor) auf D63_Nr7_8 + billiger
  Cross-Dataset-Sanity-Check. Positions-Einheit bleibt bewusst ungelöst (als
  Caveat). **Velocity bleibt offen provisorisch** (→ Ticket 08). Kanonische
  Contamination-Klassen fixiert: non-finite / frozen / incomplete-stroke /
  implausible duration / implausible sample-count (alle am Position-only-Seam
  berechenbar). **Anti-Circularity-Argument gebankt für 07:** der Floor entfernt
  *Kontamination* (physik-definiert, verteilungsunabhängig), keine
  statistischen Outlier → reinigt Stage-9-Input ohne Median/MAD zu verzerren.

## Aktueller Map-Zustand

Resolved: 01, 02, 03. Offen: 04, 05, 06, 07, 08.

**Frontier (offen, unblocked, takeable):**
- **04 Coordination approach with Fatemeh** (grilling) — buy-in vs. unilaterale
  Proposal; entblockt zusammen mit 02 die Seam-Entscheidung 05.
- **06 Additive-value evidence plan** (grilling) — durch 03 neu entblockt; Ziel
  steht schon: Masking einer Contamination-Klasse demonstrieren.
- **08 Confirm velocity-signal unit & actuator spec** (task, HITL) — Spec/Einheit
  von Supervisor/Fatemeh holen (`weekly_plan.md:36`).

**Noch blockiert:** 05 Integration seam/data contract (← 04), 07 Redundancy-
defense argument (← 06).

**Fog (Not yet specified):** finale Hand-off-Spec-Assembly, Engineer-Usability-
Kriterien, Prototype der integrierten Pre-Stage.

**Out of scope:** Ausführung der Threshold-Re-Derivation, Integrations-Code
schreiben, Fatemehs Stages 8-10 umbauen.

## Nächste Schritte

- `/wayfinder` im **Work-Modus** auf die Map ansetzen; nächstes Frontier-Ticket
  in Reihenfolge ist **04 Coordination with Fatemeh** (oder direkt 06 / 08).
- Regel: **max. 1 Nicht-Research-Ticket pro Session** resolven.
- Für Parquet immer `/home/ita/ERA-NAS/.venv/bin/python`, lazy reads, nie die
  819 MB `cycles.csv` (immer `cycles.parquet`).

## Wichtige Dateien

- Map: `.scratch/t1000-contribution/map.md`
- Tickets: `.scratch/t1000-contribution/issues/01..08-*.md`
- Kontext: `docs/approach_comparison.md`, `docs/pipeline_structure.md`,
  `docs/MasterThesis_usefulness_criteria_analysis.md`
- Datenartefakte für Pillar: `outputs/D63_Nr7_8/Versuch1/20260720_080516/`
  (`timestamp_analysis/statistics.csv`, `cycles/cycles.parquet`)
