# Handoff: Pipeline Stage Overview (standalone HTML reference)

Date: 2026-07-21
Workspace: `/home/ita/t1000`
Prompt executed: `t1000/copilot_prompt_pipeline_stage_overview.md`

## Was gemacht wurde

- Den Prompt `copilot_prompt_pipeline_stage_overview.md` ausgeführt:
  eine **einzelne, eigenständige HTML-Datei** erzeugt, die alle 11 Stufen
  von Fatemehs ERA-Preprocessing-Pipeline (V2.0) visuell erklärt.
- Ergebnis: **`/home/ita/t1000/pipeline_stage_overview.html`**
  (self-contained: CSS im `<style>`, JS im `<script>`, keine eigenen
  externen Assets; nur Google Fonts als optionale Enhancement, offline
  lauffähig). Dark Theme, vertikaler Pipeline-Flow 1→11, Status-Filter-
  Buttons, Legende, Meta-Zeile verbatim.

## Ground Truth — gegen Code verifiziert

Quellen: Fatemehs Pipeline unter `/home/ita/MasterThesis`
(Code + `docs/architecture_decisions.md`, `docs/implementation_log.md`,
`configs/example_pipeline.yaml`). Konkret bestätigt:

- **Stage 4** Session Detection: `DEFAULT_SESSION_GAP_SECONDS = 3600.0`
  in `src/preprocessing/session_detection.py`, config-überschreibbar via
  `session_gap_seconds`. ADR-006 akzeptiert nur den 1-h-Ansatz, nicht den
  konkreten Wert → *Justified (mechanism) + Inconsistent (value)*.
- **Stage 5** Cycle Detection: `movement_threshold = 1.0` in
  `src/preprocessing/cycle_detection.py` → `Position > 1.0`.
  ADR-007 begründet die Positions-Referenz → *Justified (signal) +
  Provisional (threshold)*.
- **Stage 8** Rule Generation: `median_mad`, `mad_z_limit = 3.5`,
  Quantil-Fallback `0.01/0.99`, `reference_population: all_profiled_cycles`
  (`src/preprocessing/validation_rule_generation.py`, config-yaml) →
  *Statistically derived (not health-validated)*.
- **Stage 9** Dataset Validation: Vibration = `optional_duty_cycled`
  (ESP32 duty-cycled), Referenzpopulation `all_profiled_cycles` ohne
  Healthy-Subset (`src/preprocessing/dataset_validation.py`) →
  *Justified (core) + Structural (vibration) + Unjustified (ref. pop.)*.

## Discrepancies (sichtbar geflaggt, nicht aufgelöst)

- **Stage 5:** Log §8 nennt typische Zyklusdauer **~3.1 s**, Projekt-
  kontext geht von **1.81 s** Round-trip aus → als ⚠-Note gezeigt.
- **Stage 4:** Mechanismus vs. Wert (3600 s nicht hergeleitet).
- **Stage 9:** Referenzpopulation nicht als „healthy" verifiziert.

## Bewusst NICHT enthalten (out of scope laut Prompt)

Gap-Analyse, Action-Items, Standstill/Velocity-Open-Items-Tabelle.

## Offene / mögliche nächste Schritte

- Datei im Browser sichten und ggf. an die reale Confluence-Seite
  „Data Preprocessing — Criteria Maturity & Alignment Overview" verlinken
  (aktuell Platzhalter-Anker `#`).
- Falls die 3.1 s/1.81 s-Frage geklärt wird: Discrepancy-Note in
  Stage 5 aktualisieren.
- Optional: identische Ground-Truth-Prüfung wiederholen, falls Fatemeh
  die Defaults (3600 s / 1.0 / 3.5) im Code ändert.

## Wichtige Dateien

- `/home/ita/t1000/pipeline_stage_overview.html` (Output)
- `/home/ita/t1000/copilot_prompt_pipeline_stage_overview.md` (Prompt)
- `/home/ita/MasterThesis/src/preprocessing/{session_detection,cycle_detection,validation_rule_generation,dataset_validation}.py`
- `/home/ita/MasterThesis/configs/example_pipeline.yaml`
- `/home/ita/MasterThesis/docs/architecture_decisions.md` (ADR-006/007)
- `/home/ita/MasterThesis/docs/implementation_log.md`

## Suggested skills (für die nächste Session)

- **codebase-design** — falls die Build-Pipeline im MasterThesis-Repo
  umstrukturiert oder ein Stage-Interface vertieft werden soll.
- **domain-modeling** — um ERA-Domänenbegriffe (Session, Cycle,
  Movement Threshold, MAD-Limit) als ubiquitäre Sprache festzuhalten.
- **grilling** — um die offenen Zahlenwerte (3600 s, 1.0, 3.5) und die
  1.81 s/3.1 s-Diskrepanz vor einer Entscheidung stressgetestet zu
  hinterfragen.
