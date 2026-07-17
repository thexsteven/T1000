# Handoff: Actuator Lifetime Dashboard (D32/Versuch1)

Date: 2026-07-16
Workspace: `/home/ita/t1000`
Data source: `/home/ita/data/ERA/D32_Nr13_14_15`

## Aktueller Stand

- Ich habe den eingebetteten Dashboard-Bericht unter
  `/home/ita/ERA-NAS/reports/t1000/dashboard_template.html` analysiert.
- Die Kernpipeline besteht aus drei Stufen in `t1000/cycle_overlay/`:
  1. `extract_cycle_stats.py` — Roh-Parquetdaten zu einer Zeile pro Zyklus
     aggregieren (8,66 Mio. Zyklen).
  2. `build_dashboard_data.py` — aus den Zyklusstatistiken zwei kompakte
     Artefakte erstellen:
     - `trend.json` (3.000 Buckets, Mittelwert + p10/p90 pro Kennzahl)
     - `pool.json` (1.500 repräsentativ verteilte Zyklen mit
       Wellenformen/Metadaten)
     - `meta.json` (Gesamtzahlen, Zeitraum, Pool-Größe)
  3. `build_html.py` — diese JSON-Dateien in die HTML-Vorlage injizieren
     und die finale Single-File-Webseite erzeugen.
- Ich habe drei erklärende Markdown-Dateien in `/home/ita/t1000/`
  angelegt:
  - `dashboard_architecture.md`
  - `dashboard_visualization_review.md`
  - `dashboard_presentation_plan_de.md`
- Ich habe die Frage beantwortet, ob sich der Pool dynamisch wechseln
  lässt: Der Overview-Tab zeigt bereits aggregierte Daten aller aktiven
  Zyklen. Die Vergleichsansicht ist jedoch auf den zur Build-Zeit
  erstellten Pool von 1.500 Zyklen beschränkt. Ein anderes Pool-Set
  erfordert eine Neugenerierung.

## Wichtige Erkenntnisse

- Die aktuelle Architektur ist gut geeignet für einen großen Datensatz:
  Sie trennt die Trend-Analyse (vollständige aktive Zyklen) von der
  Detailanalyse (repräsentative Stichprobe) und ermöglicht ein
  offline-generiertes Single-File-Dashboard.
- Der Ansatz ist transparent: Der Trend wird nicht einfach aus einem
  kleinen Sample erzeugt, sondern als Bucketed-Auswertung aller aktiven
  Zyklen. Der Pool ist hingegen als Vertretersubset gekennzeichnet.
- Hauptgrenzen sind:
  - die Pool-Beschränkung auf 1.500 Zyklen,
  - das Fehlen automatischer Anomalie-/Change-Point-Erkennung,
  - fehlende Ereignisannotation für Pausen/Wartung,
  - die statische Build-Pipeline ohne zentralen Orchestrierungskript.

## Vorschläge / nächste Schritte

- Falls gewünscht: `build_dashboard_data.py` erweitern, um andere
  Pool-Auswahlmodi zu unterstützen (z. B. neue Sampling-Strategien,
  zeitlich fokussierte Subsets, manuell definierte Zykluslisten).
- Zusätzliche Dashboard-Funktionen:
  - Ereignismarkierungen für Pausen/Wartungsintervalle im Trendchart,
  - einfache Ausreißer- oder Veränderungspunkte-Erkennung,
  - Heatmap- oder Dichteansicht für sehr viele Vergleichszyklen.
- Operativ: ein einzelnes Top-Level-Skript oder Makefile im
  `t1000/cycle_overlay/`-Verzeichnis einrichten, das alle drei Stufen
  nacheinander ausführt.
- Dokumentation: die erstellten Markdown-Dateien nutzen, um den
  Betreuern auf Deutsch den Build-Prozess und die Stärken/Schwächen zu
  erläutern.

## Wichtige Dateien

- `/home/ita/ERA-NAS/reports/t1000/dashboard_template.html`
- `/home/ita/t1000/cycle_overlay/extract_cycle_stats.py`
- `/home/ita/t1000/cycle_overlay/build_dashboard_data.py`
- `/home/ita/t1000/cycle_overlay/build_html.py`
- `/home/ita/t1000/dashboard_architecture.md`
- `/home/ita/t1000/dashboard_visualization_review.md`
- `/home/ita/t1000/dashboard_presentation_plan_de.md`
