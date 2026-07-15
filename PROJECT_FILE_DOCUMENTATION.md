# Projektdokumentation: t1000 – ERA Watch Data Analysis

> Diese Datei dokumentiert **jede relevante Datei** im Repository `t1000`,
> erklärt die verwendeten Dateiendungen und beschreibt, wie die Teile des
> Projekts zusammenarbeiten. Generierte/virtuelle Umgebungen (`.venv`)
> wurden von der Datei-für-Datei-Dokumentation ausgeschlossen und nur kurz
> erwähnt.

## Überblick

Dieses Repository ist der Datenanalyse-Teil einer Praxissemesterarbeit
(DHBW, bei Emerson) im Kontext "ERA" – der Analyse von Prüfstands-
Aufzeichnungsdaten (Parquet, hive-partitioniert) zu Zyklus-Timing und
Datenqualität. Konkret enthält der aktuelle Stand des Repos ein einzelnes
Unterprojekt, `cycle_overlay/`, das aus rohen Sensordaten eines
Dauerlauf-Versuchs (D32/Versuch1, ~6 Monate Betrieb, ~8,66 Mio.
Aktuator-Zyklen) zwei HTML-Reports erzeugt: einen einfachen
Cycle-Overlay-Report und ein interaktives "Actuator Lifetime Dashboard".

Es handelt sich **nicht** um eine Software-Anwendung mit Backend/Frontend
im klassischen Sinn, sondern um eine Kette von Python-Skripten
("Datenpipeline"), die aus großen Parquet-Dateien kompakte JSON-Artefakte
erzeugt und diese in eine selbstständig lauffähige HTML-Datei einbettet.

Das Repository ist **kein Git-Repository** (kein `.git`-Ordner vorhanden).

---

## 1. Dateitypen und Endungen

| Endung | Bedeutung allgemein | Verwendung in diesem Projekt | Kategorie |
|---|---|---|---|
| `.md` | Markdown-Dokumentation, für Menschen lesbar | Projektanleitung für KI-Agenten (`AGENTS.md`) und Session-Handoffs (`session-handoffs/*.md`) | Dokumentation |
| `.py` | Python-Quellcode | Die gesamte Datenpipeline (Extraktion, Aggregation, HTML-Erzeugung) ist in Python/DuckDB/Pandas/Plotly geschrieben | Quellcode |
| `.html` | HTML-Dokument, im Browser darstellbar | Sowohl Eingabe-Template (`dashboard_template.html`) als auch fertige, generierte Reports (`cycle_overlay_report.html`, `actuator_lifetime_dashboard.html`) | Quellcode (Template) / Build-Artefakt (generierte Reports) |
| `.json` | Strukturierte Textdaten (JavaScript Object Notation) | Kompakte, für den Browser aufbereitete Datenauszüge (`meta.json`, `trend.json`, `pool.json`), die ins HTML-Template injiziert werden | Daten (generiert) |
| `.parquet` | Spaltenorientiertes Binärformat für große Datenmengen (Apache Arrow/Parquet) | Speichert sowohl Rohdaten-Auszüge (z. B. `counter_v1.parquet`) als auch aggregierte Zwischenergebnisse (`cycle_stats_full.parquet`, `vel_*`, `pos_*`) | Daten (Cache/Build-Artefakt) |
| `.pkl` | Python-Pickle, serialisiertes Python-Objekt (hier: Listen von Zeitfenster-Tupeln) | Zwischenspeicherung der Zyklusgrenzen ("boundaries") für `build_report.py` | Daten (Cache) |

Es gibt in diesem Projekt **keine** der folgenden im Prompt genannten
Dateiendungen/Dateien: `.js` (eigenständig), `.ts`/`.tsx`, `.css`
(eigenständig), `.env`, `.yml`/`.yaml`, `.sql` (eigenständig, SQL steckt
nur als String in Python-Code), `.db`, `.txt`, `Dockerfile`,
`requirements.txt`, `package.json`, `tsconfig.json`. Das Projekt hat also
**keine explizite Dependency-Datei** und **kein Containerization-Setup**
im Repo selbst (siehe Abschnitt 8, "Empfohlene Ergänzungen").

JavaScript und CSS existieren nur **inline** innerhalb der `.html`-Dateien
(nicht als eigene Dateien) – siehe `dashboard_template.html`.

---

## 2. Dateiübersicht

### `AGENTS.md`

**Dateityp:** Markdown-Dokumentation
**Kategorie:** Dokumentation
**Aufgabe:** Zentrale Betriebsanleitung für KI-Agenten (z. B. Copilot CLI/Claude), die in diesem Repo arbeiten. Definiert Pflichtschritte, Umgebungsdetails und Konventionen.
**Inhalt:** Vier Abschnitte: (1) Pflicht, zuerst `session-handoffs/LATEST.md` zu lesen; (2) Projektkontext (Praxissemesterarbeit, ERA-Datensätze); (3) Umgebungsdetails (kein Admin, SSH-Remote "flmc-ai", zu verwendendes venv `/home/ita/ERA-NAS/.venv/bin/python`, externe read-only Datenverzeichnisse `/home/ita/ERA`, `/home/ita/ERA-NAS`); (4) Konventionen für Session-Handoffs (Namensschema, Symlink-Pflege) und Output (alle generierten Dateien müssen innerhalb von `t1000/` bleiben).
**Warum benötigt:** Ohne diese Datei würde ein neuer Agent/Entwickler wichtigen Kontext (z. B. welches Python-venv funktioniert, wo die Rohdaten liegen, dass Handoffs zuerst zu lesen sind) verlieren und riskiert, außerhalb des erlaubten Verzeichnisses zu schreiben oder ein kaputtes System-Python zu benutzen.
**Abhängigkeiten:** Verweist auf `session-handoffs/LATEST.md` sowie auf externe, nicht in diesem Repo enthaltene Pfade (`/home/ita/ERA`, `/home/ita/ERA-NAS`).
**Hinweise:** Nicht als reine Doku behandeln – enthält handlungsrelevante Regeln (z. B. "outside `t1000/` darf nichts geschrieben werden"), die bei jeder neuen Aufgabe zu respektieren sind.

---

### `session-handoffs/LATEST.md`

**Dateityp:** Symlink auf eine Markdown-Datei
**Kategorie:** Dokumentation
**Aufgabe:** Zeigt immer auf den zuletzt geschriebenen Handoff im Ordner `session-handoffs/`, sodass Agenten nicht raten müssen, welche Datei aktuell ist.
**Inhalt:** Kein eigener Inhalt – reiner Verweis (derzeit auf `handoff-20260715-064618-actuator-lifetime-dashboard.md`).
**Warum benötigt:** Ermöglicht kontinuierlichen Wissenstransfer zwischen Sitzungen ohne Chat-Historie; ist laut `AGENTS.md` der erste Pflicht-Lesepunkt jeder neuen Session.
**Abhängigkeiten:** Muss nach jeder Session per `ln -sf` aktualisiert werden.
**Hinweise:** Beim Anlegen eines neuen Handoffs unbedingt den Symlink erneuern, sonst zeigt er auf veraltete Informationen.

---

### `session-handoffs/handoff-t1000-cycle-overlay-20260713.md`

**Dateityp:** Markdown-Dokumentation
**Kategorie:** Dokumentation
**Aufgabe:** Ältester Handoff; dokumentiert die erste Version des Cycle-Overlay-Reports (`build_report.py` / `cycle_overlay_report.html`).
**Inhalt:** Entscheidungen zur Zyklusdefinition (Magnetschalter_Counter), fünf Report-Ansichten, verwendete Signal-IDs, offene Punkte.
**Warum benötigt:** Historischer Kontext, warum `build_report.py` so aufgebaut ist wie es ist (z. B. Pausenerkennung, Zeitfenster-Auswahl).
**Abhängigkeiten:** Bezieht sich auf `cycle_overlay/build_report.py` und dessen Output-Dateien.
**Hinweise:** Nicht mehr der aktuelle Stand – für den neuesten Stand gilt `LATEST.md`.

---

### `session-handoffs/handoff-20260713-121411-era-data-analysis.md`

**Dateityp:** Markdown-Dokumentation
**Kategorie:** Dokumentation
**Aufgabe:** Zweiter Handoff zur allgemeinen ERA-Datenanalyse (Datenstruktur, Datenqualität, Cycle-Timing-Untersuchungen), Vorarbeit zum Dashboard.
**Inhalt:** Vermutlich Erkenntnisse zu Signal-Metadaten (`units.parquet`), Datenfluenz und Struktur der hive-partitionierten Parquet-Dateien (nicht vollständig neu ausgewertet in dieser Dokumentation – siehe Datei direkt für Details).
**Warum benötigt:** Grundlage/Kontext für spätere Analyseentscheidungen (z. B. welche Signal-IDs welche physikalische Bedeutung haben).
**Abhängigkeiten:** Bezieht sich auf externe Datensätze unter `/home/ita/ERA`.
**Hinweise:** Chronologisch vor dem Dashboard-Handoff; für aktuellen Stand `LATEST.md` verwenden.

---

### `session-handoffs/handoff-20260715-064618-actuator-lifetime-dashboard.md`

**Dateityp:** Markdown-Dokumentation
**Kategorie:** Dokumentation
**Aufgabe:** Aktuellster Handoff (Ziel von `LATEST.md`). Beschreibt vollständig den Bau des "Actuator Lifetime Dashboard".
**Inhalt:** Aufbau der 3-stufigen Pipeline (`extract_cycle_stats.py` → `build_dashboard_data.py` → `build_html.py`), Datenfakten (8.658.098 Zyklen, Einheiten, Sampling-Raten), Scope-Entscheidung (nur Versuch1), implementierte Dashboard-Features, Validierungsvorgehen (Playwright/Chromium headless), offene nächste Schritte (Versuch2/Versuch3, Vibrationssignale).
**Warum benötigt:** Zentrale Referenz, um die aktuelle Pipeline und das Dashboard ohne erneutes Reverse-Engineering zu verstehen und fortzusetzen.
**Abhängigkeiten:** Beschreibt direkt `cycle_overlay/extract_cycle_stats.py`, `build_dashboard_data.py`, `build_html.py`, `dashboard_template.html` und deren Outputs.
**Hinweise:** Enthält wichtige Warnungen (z. B. Einheiten "wie in `units.parquet`" trotz physikalisch ungewöhnlicher Größenordnungen – nicht eigenmächtig umskalieren).

---

### `cycle_overlay/build_report.py`

**Dateityp:** Python-Quellcode
**Kategorie:** Quellcode
**Aufgabe:** Erzeugt den **ersten, einfacheren** HTML-Report (`output/cycle_overlay_report.html`) mit fünf Ansichten von Drive-Geschwindigkeit/-Position: (1) ein repräsentativer Einzelzyklus, (2) 100 aufeinanderfolgende Zyklen überlagert, (3) ~100 über die gesamte Laufzeit verteilte Zyklen überlagert, (4) 100 aufeinanderfolgende Zyklen als "Filmstreifen" in echter Zeit, (5) 100 zufällige aktive Zyklen als Filmstreifen.
**Inhalt:** Funktionen `assign_cycle()` (ordnet Rohdaten-Zeilen per `searchsorted` einem Zyklus zu), `build_single_cycle_figure()`, `build_overlay_figure()` (mit Viridis-Farbverlauf via `_colorscale()`), `_break_on_cycle()` (fügt NaN-Zeilen ein, damit Plotly-Linien nicht über Zyklusgrenzen hinweg verbunden werden), `build_row_figure()` (Filmstreifen-Layout, Modus `contiguous` vs. `filmstrip`), `main()` (baut alle 5 Plotly-Figuren und schreibt sie in eine gemeinsame HTML-Datei).
**Warum benötigt:** War der erste Explorationsschritt, um die Zyklusstruktur der Drive-Signale visuell zu verstehen, bevor das größere Lifetime-Dashboard gebaut wurde. Wird laut aktuellem Handoff nur noch als Referenz für Datenlade-Muster verwendet, nicht mehr aktiv weiterentwickelt.
**Abhängigkeiten:** Liest die vorbereiteten Parquet-/Pickle-Dateien `output/{vel,pos}_{single,consec,spread,random}.parquet` und `output/{single,consec,spread,random}_boundaries_v1.pkl` (nicht im Skript selbst erzeugt – vermutlich in einer früheren, hier nicht vorhandenen Vorverarbeitung entstanden). Nutzt `plotly`, `pandas`, `numpy`, `pickle`.
**Hinweise:** Erwartet, dass die o. g. Parquet/Pickle-Dateien bereits in `output/` existieren; führt selbst keine Rohdaten-Extraktion aus `/home/ita/data/ERA/...` durch. Bei fehlenden Eingabedateien schlägt das Skript fehl.

---

### `cycle_overlay/extract_cycle_stats.py`

**Dateityp:** Python-Quellcode
**Kategorie:** Quellcode
**Aufgabe:** **Schritt 1** der Dashboard-Pipeline. Berechnet für jeden der ~8,66 Mio. Zyklen (definiert über das `Magnetschalter_Counter`-Signal) Aggregatstatistiken (min/max/mean/peak) für 7 kontinuierliche Signale: Geschwindigkeit, Position, Strom, Druck, Motor-/Spindelmutter-/Festlager-Temperatur.
**Inhalt:** Dictionary `SIGNALS` (Signal-Kurzname → UUID der Signal-ID im hive-partitionierten Parquet-Datensatz), Funktion `main()`, die per **DuckDB ASOF JOIN** jede Rohmessung der zeitlich letzten Zyklusgrenze zuordnet und je Zyklus `n/vmin/vmax/vavg/vpeak` aggregiert, ohne die ~300 Mio. Rohzeilen je Signal komplett in den Speicher zu laden.
**Warum benötigt:** Reduziert die riesige Rohdatenmenge auf eine handhabbare Tabelle mit einer Zeile pro Zyklus – die Grundlage für alle weiteren Aggregationsschritte (Trend-Chart, Pool-Sampling).
**Abhängigkeiten:** Liest `output/counter_v1_annot.parquet` (Zyklusgrenzen + Pausenerkennung, aus einer früheren Session übernommen) und die externen Rohdaten unter `/home/ita/data/ERA/D32_Nr13_14_15/signal_data_point.parquet/signal_id=<uuid>/*.parquet`. Schreibt `output/cycle_stats_full.parquet`. Wird von `build_dashboard_data.py` konsumiert.
**Hinweise:** Laufzeit ca. 1 Minute; erzeugt eine ~472 MB große Parquet-Datei. Muss nur neu ausgeführt werden, wenn sich Signaldefinitionen oder Zyklusgrenzen ändern – nicht bei jedem Dashboard-Rebuild.

---

### `cycle_overlay/build_dashboard_data.py`

**Dateityp:** Python-Quellcode
**Kategorie:** Quellcode
**Aufgabe:** **Schritt 2** der Pipeline. Erstellt aus `cycle_stats_full.parquet` drei kompakte, browser-taugliche JSON-Artefakte: `trend.json` (3.000 chronologische Buckets mit Mittelwert/P10/P90 je Metrik für den Overview-Trendchart), `pool.json` (1.500 gleichmäßig über die Laufzeit verteilte Zyklen inkl. voll aufgelöster Wellenformen und abgeleiteter Kennwerte für den Vergleichsmodus) und `meta.json` (Zusammenfassungszahlen).
**Inhalt:** Konstanten `N_BUCKETS=3000`, `POOL_SIZE=1500`, `BATCH=150`; Dict `WAVE_SIGNALS`; Liste `METRICS`; Funktionen `build_trend()` (Bucket-Bildung + Perzentile), `loop_area()` (Shoelace-Formel für eine Strom-vs-Position-"Hystereseschleifen"-Fläche, da kein echtes Kraft/Drehmoment-Signal existiert), `build_pool()` (extrahiert Wellenformen batchweise per DuckDB-Abfrage mit vielen OR-verknüpften Zeitfenstern und berechnet abgeleitete Kennwerte je Pool-Zyklus inkl. Abweichung vom Referenzzyklus), `main()`.
**Warum benötigt:** Macht es möglich, ~8,66 Mio. Zyklen sinnvoll in einer einzigen HTML-Datei darzustellen, ohne alle Rohdaten einzubetten – Kernstück der Daten-Kompression für das Dashboard.
**Abhängigkeiten:** Liest `output/cycle_stats_full.parquet` (von `extract_cycle_stats.py`) und `output/counter_v1_annot.parquet`. Schreibt `output/trend.json`, `output/pool.json`, `output/meta.json`. Wird von `build_html.py` konsumiert.
**Hinweise:** Laufzeit ca. 1 Minute; Wellenform-Extraktion nutzt Batches von 150 nicht-zusammenhängenden Zeitfenstern pro SQL-Abfrage für Performance. Bei Änderung von `POOL_SIZE`/`N_BUCKETS` ändert sich die Dateigröße der resultierenden JSONs deutlich (aktuell `pool.json` ~4,6 MB, `trend.json` ~2,3 MB).

---

### `cycle_overlay/build_html.py`

**Dateityp:** Python-Quellcode
**Kategorie:** Quellcode / Build-Skript
**Aufgabe:** **Schritt 3** der Pipeline. Fügt die drei JSON-Dateien als Platzhalter-Ersetzung in `dashboard_template.html` ein und erzeugt daraus die finale, eigenständige Datei `output/actuator_lifetime_dashboard.html`.
**Inhalt:** Liest `dashboard_template.html` sowie `meta.json`, `trend.json`, `pool.json`; ersetzt die String-Platzhalter `__META_JSON__`, `__TREND_JSON__`, `__POOL_JSON__` durch den jeweiligen JSON-Text; schreibt das Ergebnis und gibt die Dateigröße in MB aus.
**Warum benötigt:** Letzter Schritt, der aus Template + Daten ein einziges, portables HTML-Artefakt macht, das ohne lokalen Server per Doppelklick geöffnet werden kann.
**Abhängigkeiten:** Direkt abhängig von `dashboard_template.html` und den drei JSON-Outputs von `build_dashboard_data.py`.
**Hinweise:** Sehr einfaches String-Replace – falls die JSON-Inhalte selbst die Platzhalter-Strings enthalten würden, könnte es zu Fehlern kommen (unwahrscheinlich, aber bei Änderungen am Template beachten). Laufzeit: quasi instant.

---

### `cycle_overlay/dashboard_template.html`

**Dateityp:** HTML mit eingebettetem CSS und JavaScript
**Kategorie:** Quellcode (Template)
**Aufgabe:** Enthält das vollständige UI/UX-Gerüst des "Actuator Lifetime Dashboard" (Layout, Styling, Interaktivität) mit drei Platzhaltern (`__META_JSON__`, `__TREND_JSON__`, `__POOL_JSON__`), die erst durch `build_html.py` mit echten Daten befüllt werden.
**Inhalt:** CSS-Variablen für Light-/Dark-Theme; Header mit Meta-Info und Theme-Umschalter; Tab-Navigation ("Overview" und "Cycle Comparison"); JavaScript-Funktionen u. a. `colorFor()`/`shadeColor()` (Okabe-Ito farbenblind-sichere Palette, zyklisch mit Helligkeitsverschiebung), `buildStatCards()` (8 Lifetime-Kennzahlkarten), `buildTrendPicker()`/`renderTrendChart()` (Trendchart mit Metrik-Auswahl-Chips, Min-Max-Normalisierung bei Mehrfachauswahl, P10–P90-Band), `nearestPoolCycle()` (Snap-to-nearest bei Zyklus-ID-Suche), `buildChannelPicker()`, `addCycles()`, `refreshCompare()`, `renderLegendList()` (Klick zum Hervorheben, Shift-Klick zum Ausblenden), `renderChannelPlots()` (5 synchronisierte Subplots), `renderMetricsTable()` (abgeleitete Kennwerte inkl. Differenz zum Referenzzyklus).
**Warum benötigt:** Trennt Layout/Logik (dieses Template) von den Daten (JSON-Dateien) – ermöglicht es, das Dashboard-Design zu ändern, ohne die Datenpipeline neu laufen zu lassen (nur `build_html.py` erneut ausführen).
**Abhängigkeiten:** Lädt Plotly.js 2.35.2 von einem CDN (`cdn.plot.ly`) – erfordert also Internetzugang beim **Öffnen** des fertigen Reports (nicht beim Bauen). Wird von `build_html.py` gelesen und durch die JSON-Daten zu `output/actuator_lifetime_dashboard.html` kombiniert.
**Hinweise:** Größere UI-Änderungen (z. B. neue Metriken/Kanäle) müssen konsistent mit den Datenfeldern erfolgen, die `build_dashboard_data.py` in `pool.json`/`trend.json` erzeugt – Template und Datenpipeline sind eng gekoppelt.

---

### `cycle_overlay/output/actuator_lifetime_dashboard.html`

**Dateityp:** HTML (generiert, ~6,9 MB)
**Kategorie:** Build-Artefakt / finales Deliverable
**Aufgabe:** Das fertige, eigenständig lauffähige Dashboard – Endprodukt der gesamten Pipeline. Kann direkt im Browser geöffnet werden.
**Inhalt:** `dashboard_template.html` mit eingebetteten `meta`/`trend`/`pool`-Daten als inline JavaScript-Konstanten.
**Warum benötigt:** Ist das eigentliche Ergebnis/Deliverable der Analysearbeit für den Nutzer bzw. Betreuer.
**Abhängigkeiten:** Wird ausschließlich von `build_html.py` erzeugt; sollte nicht händisch editiert werden (Änderungen gehen bei nächstem Build verloren).
**Hinweise:** Generierte Datei – bei jeder erneuten Ausführung der Pipeline wird sie überschrieben. Nicht versionskontrolliert committen als "Quelle der Wahrheit", sondern die Pipeline-Skripte.

---

### `cycle_overlay/output/cycle_overlay_report.html`

**Dateityp:** HTML (generiert, ~1,2 MB)
**Kategorie:** Build-Artefakt
**Aufgabe:** Älterer, einfacherer Report mit den fünf Drive-Overlay-Ansichten aus `build_report.py`.
**Inhalt:** Fünf eingebettete Plotly-Diagramme (Einzelzyklus, Overlay konsekutiv, Overlay verteilt, Filmstreifen konsekutiv, Filmstreifen zufällig) plus erklärender Text.
**Warum benötigt:** Diente als erste visuelle Exploration und als Referenz-Layout für das spätere, größere Dashboard.
**Abhängigkeiten:** Erzeugt von `build_report.py`; lädt Plotly.js ebenfalls per CDN.
**Hinweise:** Wird laut aktuellem Handoff nicht mehr aktiv weiterentwickelt, nur noch als Referenz behalten.

---

### `cycle_overlay/output/meta.json`

**Dateityp:** JSON (generiert, ~4 KB)
**Kategorie:** Daten
**Aufgabe:** Kompakte Zusammenfassung der Gesamtdatensatz-Kennzahlen für die Kopfzeile/Statuspille des Dashboards.
**Inhalt:** `total_cycles` (8.658.098), `active_cycles` (7.690.500), `start_time`/`end_time` (2025-12-18 bis 2026-06-20), `pool_size` (1500), `n_buckets` (3000).
**Warum benötigt:** Liefert dem Dashboard die globalen Kennzahlen, ohne dass der Browser die volle Datenmenge auswerten muss.
**Abhängigkeiten:** Erzeugt von `build_dashboard_data.py`; konsumiert von `build_html.py` (Platzhalter `__META_JSON__`) und im Browser von `dashboard_template.html`.
**Hinweise:** Muss synchron mit `trend.json`/`pool.json` neu erzeugt werden.

---

### `cycle_overlay/output/trend.json`

**Dateityp:** JSON (generiert, ~2,3 MB)
**Kategorie:** Daten
**Aufgabe:** Liefert die Datenbasis für den Lifetime-Trendchart im "Overview"-Tab.
**Inhalt:** 3.000 chronologisch geordnete Buckets, je mit `cycle_index`, Zeitstempel `t`, `n_cycles` und pro Metrik einem Objekt `{mean, p10, p90}` für 11 Metriken (u. a. Peak-Geschwindigkeit, Hub/Position, Peak-Strom, Druck, Temperaturen, Zyklusdauer).
**Warum benötigt:** Ermöglicht die Darstellung des Trends über alle 7,69 Mio. aktiven Zyklen, ohne diese einzeln an den Browser zu übertragen.
**Abhängigkeiten:** Erzeugt von `build_dashboard_data.py` (Funktion `build_trend()`) aus `cycle_stats_full.parquet`; konsumiert von `build_html.py` und `renderTrendChart()` im Template.
**Hinweise:** Bei Änderung der Metrik-Liste (`METRICS` in `build_dashboard_data.py`) muss auch das Template (`buildTrendPicker()`) angepasst werden.

---

### `cycle_overlay/output/pool.json`

**Dateityp:** JSON (generiert, ~4,6 MB)
**Kategorie:** Daten
**Aufgabe:** Liefert die 1.500 repräsentativen Zyklen mit vollaufgelösten Wellenformen für den "Cycle Comparison"-Tab.
**Inhalt:** Je Zyklus: `cycle_index`, Zeitstempel, abgeleitete Kennwerte (Dauer, Peak-Geschwindigkeit, Hub, Peak-Strom, Druck- und Temperaturmittelwerte), Wellenform-Objekte (`wave.{vel,pos,cur,prs,stemp}` mit Zeit/Wert-Arrays), `loop_area` (Strom-vs-Position-Schleifenfläche) und `dev_from_ref` (Abweichung vom ersten Pool-Zyklus als Referenz).
**Warum benötigt:** Ist die einzige Menge an Zyklen, die im Vergleichsmodus des Dashboards auswählbar/überlagerbar ist – ein bewusst begrenzter, aber repräsentativer Ausschnitt statt aller 8,66 Mio. Zyklen.
**Abhängigkeiten:** Erzeugt von `build_dashboard_data.py` (Funktion `build_pool()`); konsumiert von `build_html.py` und `addCycles()`/`renderChannelPlots()` im Template.
**Hinweise:** Zyklus-ID-Suche im Dashboard "snapt" auf den nächstgelegenen Pool-Zyklus (`nearestPoolCycle()`), da nicht jede beliebige der 8,66 Mio. IDs enthalten ist – dies ist im UI explizit kommuniziert, nicht verstecken.

---

### `cycle_overlay/output/counter_v1.parquet` und `counter_v1_annot.parquet`

**Dateityp:** Parquet (Cache, ~86 MB bzw. ~109 MB)
**Kategorie:** Daten (Cache)
**Aufgabe:** Enthalten die Rohwerte bzw. annotierten Werte (inkl. `dt`, `dist_to_pause`) des `Magnetschalter_Counter`-Signals, das die Zyklusgrenzen definiert.
**Inhalt:** Zeitreihe mit Zeitstempeln und Zählerständen; `_annot`-Version zusätzlich mit Abstand zur nächsten Pause im Betrieb.
**Warum benötigt:** Grundlage für die Zyklus-Segmentierung in sowohl `extract_cycle_stats.py` als auch (indirekt über `boundaries`) `build_dashboard_data.py`.
**Abhängigkeiten:** Aus einer früheren Session übernommen (nicht in diesem Repo neu erzeugt); wird von `extract_cycle_stats.py` und `build_dashboard_data.py` gelesen.
**Hinweise:** Laut Handoff **nicht neu generieren**, außer die Pausenerkennungslogik ändert sich – Wiederverwendung ist bewusst und dokumentiert.

---

### `cycle_overlay/output/cycle_stats_full.parquet`

**Dateityp:** Parquet (generiert, ~472 MB – größte Datei im Projekt)
**Kategorie:** Daten (Build-Zwischenartefakt)
**Aufgabe:** Eine Zeile pro Zyklus (~8,66 Mio. Zeilen) mit Aggregatwerten (n/min/max/avg/peak) für alle 7 Signale plus Zyklusdauer und Aktiv-Flag.
**Inhalt:** Spalten wie `vel_vpeak`, `pos_vmin`, `pos_vmax`, `cur_vavg`, `mtemp_vavg` usw.
**Warum benötigt:** Zentrale Zwischentabelle zwischen der teuren Rohdaten-Aggregation (Schritt 1) und der browser-tauglichen Verdichtung (Schritt 2).
**Abhängigkeiten:** Erzeugt von `extract_cycle_stats.py`; gelesen von `build_dashboard_data.py`.
**Hinweise:** Sehr groß – nicht versehentlich in ein Web-Deployment einbetten; nur als lokales Zwischenartefakt gedacht.

---

### `cycle_overlay/output/{vel,pos}_{single,consec,spread,random}.parquet` (8 Dateien)

**Dateityp:** Parquet (klein, je 4 KB–64 KB)
**Kategorie:** Daten (Eingabe für `build_report.py`)
**Aufgabe:** Vorab extrahierte Roh-Wellenformen (Geschwindigkeit `vel_*` bzw. Position `pos_*`) für die vier im ersten Report verwendeten Stichproben-Arten: ein einzelner Zyklus (`_single`), 100 konsekutive Zyklen (`_consec`), ~100 über die Laufzeit verteilte Zyklen (`_spread`), 100 zufällige aktive Zyklen (`_random`).
**Inhalt:** Zeit/Wert-Paare der jeweiligen Rohmessung.
**Warum benötigt:** Eingabedaten für `build_report.py`, das daraus die fünf Ansichten im ersten HTML-Report zeichnet.
**Abhängigkeiten:** Werden von `build_report.py` per `load()` eingelesen; die zugehörigen Zyklusgrenzen liegen in den passenden `*_boundaries_v1.pkl`-Dateien.
**Hinweise:** Ursprung dieser Dateien (welches Skript sie erzeugt hat) ist **nicht eindeutig erkennbar** in diesem Repo-Stand – vermutlich in einer früheren, nicht mehr vorhandenen Vorverarbeitungs-Session entstanden.

---

### `cycle_overlay/output/{single,consec,spread,random}_boundaries_v1.pkl` (4 Dateien)

**Dateityp:** Python-Pickle (klein, 4–8 KB)
**Kategorie:** Daten (Cache)
**Aufgabe:** Serialisierte Listen von Zyklusgrenzen-Tupeln `(start, end)` für die jeweilige Stichprobe, die `assign_cycle()` in `build_report.py` verwendet, um Rohmesspunkte einem Zyklusindex zuzuordnen.
**Inhalt:** Python-Listen mit Zeitstempel-Tupeln.
**Warum benötigt:** Notwendig, damit `build_report.py` weiß, wo jeder Zyklus beginnt/endet.
**Abhängigkeiten:** Wird von `build_report.py` per `pickle.load()` gelesen.
**Hinweise:** Pickle-Dateien sind nicht plattform-/versionsunabhängig und sollten nicht als langfristiges Datenformat verwendet werden – nur als internes Cache-Format akzeptabel.

---

### `cycle_overlay/.venv/` (generiert, nicht einzeln dokumentiert)

**Kategorie:** Generiert / externe Abhängigkeiten
Enthält eine Python-3.12-virtuelle-Umgebung mit den für die Pipeline nötigen Paketen: `duckdb`, `pandas`, `numpy`, `pyarrow`, `plotly`, `packaging`, `dateutil` u. a. Wird laut Vorgabe von der detaillierten Dokumentation ausgeschlossen, da automatisch generiert/installiert. **Wichtig:** Es existiert aktuell keine `requirements.txt`, die diese Abhängigkeiten für Dritte reproduzierbar macht (siehe Abschnitt 8).

---

## 3. Ordnerstruktur

### `/` (Repository-Wurzel)

**Zweck:** Enthält die projektweite Agenten-Anleitung und die zwei fachlichen Unterordner.
**Wichtige Dateien:** `AGENTS.md`
**Warum benötigt:** Einstiegspunkt für jede neue Bearbeitungssitzung; verweist auf alles Weitere.

### `session-handoffs/`

**Zweck:** Verlaufsprotokoll der Analyse-Sessions – jede abgeschlossene Sitzung hinterlässt einen datierten Bericht.
**Wichtige Dateien:** `LATEST.md` (Symlink), sowie drei chronologisch benannte `handoff-*.md`-Dateien.
**Warum benötigt:** Ersetzt fehlende Chat-Historie zwischen Sitzungen; macht Entscheidungen, Datenfakten und offene Punkte nachvollziehbar, ohne den Code erneut reverse-engineeren zu müssen.

### `cycle_overlay/`

**Zweck:** Das eigentliche Analyse-Unterprojekt: Python-Pipeline + Templates + generierte Reports für den D32/Versuch1-Dauerlauf.
**Wichtige Dateien:** `build_report.py` (alter Report), `extract_cycle_stats.py` → `build_dashboard_data.py` → `build_html.py` (neue Dashboard-Pipeline, in dieser Reihenfolge auszuführen), `dashboard_template.html` (UI-Template).
**Warum benötigt:** Zentraler Ort der gesamten fachlichen Logik und aller Build-Ergebnisse dieses Repo-Stands.

### `cycle_overlay/output/`

**Zweck:** Ablage aller generierten und zwischengespeicherten Daten- und HTML-Artefakte der Pipeline.
**Wichtige Dateien:** `actuator_lifetime_dashboard.html` (finales Deliverable), `cycle_stats_full.parquet` (größtes Zwischenartefakt), `meta.json`/`trend.json`/`pool.json` (Dashboard-Daten), diverse kleinere `.parquet`/`.pkl`-Dateien für den alten Report.
**Warum benötigt:** Trennt generierte/reproduzierbare Ausgaben klar vom eigentlichen Quellcode; kann bei Bedarf komplett gelöscht und aus den Skripten neu erzeugt werden (mit Ausnahme von `counter_v1_annot.parquet`, das bewusst aus einer früheren Session wiederverwendet wird).

### `cycle_overlay/.venv/` (generiert)

**Zweck:** Isolierte Python-Umgebung mit den für die Pipeline benötigten Paketen (duckdb, pandas, pyarrow, plotly, numpy).
**Warum benötigt:** Stellt sicher, dass die Pipeline mit den richtigen Paketversionen läuft, unabhängig vom System-Python (das laut `AGENTS.md` ohnehin keine passenden Pakete hat).

---

## 4. Wie das Projekt zusammenarbeitet

- **Kein klassischer "Einstiegspunkt"** wie `main.py`/`index.js` – dies ist
  eine Batch-Pipeline aus drei aufeinander aufbauenden Skripten, die
  manuell in Reihenfolge ausgeführt werden:
  1. `cycle_overlay/extract_cycle_stats.py`
  2. `cycle_overlay/build_dashboard_data.py`
  3. `cycle_overlay/build_html.py`

  Das ältere `cycle_overlay/build_report.py` ist ein separater, davon
  unabhängiger Pfad, der einen einfacheren Report erzeugt und bereits
  vorbereitete `.parquet`/`.pkl`-Dateien voraussetzt.

- **Programmfluss (Dashboard-Pipeline):**
  externe Rohdaten (`/home/ita/data/ERA/D32_Nr13_14_15/...`, außerhalb
  des Repos) → `extract_cycle_stats.py` (DuckDB-Aggregation) →
  `cycle_stats_full.parquet` → `build_dashboard_data.py` (Bucketing +
  Pool-Sampling) → `trend.json`/`pool.json`/`meta.json` →
  `build_html.py` (Template-Injektion mit `dashboard_template.html`) →
  `actuator_lifetime_dashboard.html` (fertiges, im Browser lauffähiges
  Ergebnis).

- **Konfiguration:** Es gibt keine separate Konfigurationsdatei –
  Konfigurationswerte (Signal-IDs, Bucket-/Pool-Größen, Batch-Größen,
  Pfade) sind als Konstanten direkt am Kopf der jeweiligen `.py`-Dateien
  hartkodiert (`BASE`, `SDP`, `SIGNALS`, `N_BUCKETS`, `POOL_SIZE`,
  `BATCH`).

- **Datenspeicherung/-ladung:** Parquet-Dateien übernehmen die Rolle
  einer Datenbank für Zwischenergebnisse; JSON-Dateien sind die
  "API-Antwort" fürs Frontend (das Dashboard-Template); Pickle-Dateien
  dienen nur dem alten Report als Cache für Zeitfenstergrenzen.

- **Benutzeroberfläche:** Ausschließlich `dashboard_template.html`
  (bzw. dessen generiertes Ergebnis) – kein separates Backend, keine
  API im Netzwerksinn. Alle "API-Aufrufe" passieren als einmalige
  Daten-Injektion beim Build; zur Laufzeit im Browser gibt es nur
  clientseitiges JavaScript, das auf inline-Konstanten operiert.
  Externe Netzwerkabhängigkeit besteht nur für die Plotly.js-CDN-Datei.

- **Tests/Deployment:** Es gibt keine automatisierten Tests und kein
  Deployment-Setup in diesem Repo; Validierung erfolgte laut Handoff
  manuell per Playwright/Chromium (headless) außerhalb des
  dokumentierten Dateibestands.

- **Am wichtigsten zum Verständnis:** `AGENTS.md` (Regeln),
  `session-handoffs/LATEST.md` (aktueller Stand),
  `cycle_overlay/build_dashboard_data.py` (enthält die meiste fachliche
  Logik: Bucketing, Pool-Sampling, abgeleitete Kennwerte) und
  `dashboard_template.html` (definiert, was der Nutzer tatsächlich sieht
  und tun kann).

---

## 5. Wichtigste Dateien zum Verständnis des Projekts

- `AGENTS.md`: Betriebsregeln und Umgebungsbeschreibung – ohne dies fehlt der Kontext, wie überhaupt zu arbeiten ist.
- `session-handoffs/LATEST.md`: Aktueller Projektstand, Entscheidungen und offene Punkte.
- `cycle_overlay/extract_cycle_stats.py`: Erste Aggregationsstufe – bestimmt, welche Rohsignale/Metriken überhaupt verfügbar sind.
- `cycle_overlay/build_dashboard_data.py`: Fachlich dichteste Datei – Bucketing-Logik, Pool-Sampling, abgeleitete Kennwerte (u. a. `loop_area()`).
- `cycle_overlay/build_html.py`: Verbindet Daten und Template zum finalen Ergebnis.
- `cycle_overlay/dashboard_template.html`: Definiert die gesamte Nutzerinteraktion mit den Daten.
- `cycle_overlay/output/actuator_lifetime_dashboard.html`: Das eigentliche Endergebnis/Deliverable für Betrachter ohne Entwicklerhintergrund.

---

## 6. Dateien, die vorsichtig geändert werden sollten

- **`cycle_overlay/extract_cycle_stats.py`** – Änderungen an `SIGNALS`
  (Signal-IDs) oder der ASOF-JOIN-Logik wirken sich auf **alle**
  nachgelagerten Artefakte aus (`cycle_stats_full.parquet`, `trend.json`,
  `pool.json`, das gesamte Dashboard). Falsche Signal-IDs führen zu
  stillschweigend falschen/leeren Metriken.
- **`cycle_overlay/build_dashboard_data.py`** – Änderungen an `METRICS`,
  `N_BUCKETS` oder `POOL_SIZE` verändern die JSON-Struktur; das Template
  (`dashboard_template.html`) muss dann parallel angepasst werden, sonst
  brechen `buildTrendPicker()`/`renderTrendChart()`/`renderChannelPlots()`.
- **`cycle_overlay/dashboard_template.html`**: Die Platzhalter-Strings
  `__META_JSON__`, `__TREND_JSON__`, `__POOL_JSON__` dürfen nicht
  verändert/umbenannt werden, ohne `build_html.py` entsprechend
  anzupassen – sonst schlägt die Injektion fehl oder das Dashboard bleibt
  leer.
- **`cycle_overlay/output/counter_v1_annot.parquet`**: Wird bewusst aus
  einer früheren Session wiederverwendet; ein versehentliches Löschen
  oder Überschreiben mit anderer Pausenerkennungslogik ändert stillschweigend
  die Zyklusdefinition für die gesamte Pipeline.
- **Einheiten-Handling**: Laut Handoff wurden Einheiten bewusst **nicht**
  umskaliert, obwohl sie physikalisch ungewöhnlich wirken (z. B.
  Geschwindigkeit ~±70.000). Eigenmächtiges "Korrigieren" dieser Werte in
  einem der drei Pipeline-Skripte ohne Rücksprache würde der
  dokumentierten Projektkonvention widersprechen.

---

## 7. Empfohlene Ergänzungen

Im aktuellen Repo-Stand fehlen einige häufig erwartete Dateien:

| Fehlende Datei | Empfehlung |
|---|---|
| `README.md` | Fehlt komplett auf Repo-Ebene. Empfehlung: kurze README mit Projektbeschreibung, Pipeline-Ausführungsreihenfolge (siehe Abschnitt 4) und Link auf `AGENTS.md`/`session-handoffs/LATEST.md`. |
| `.gitignore` | Fehlt; zudem ist das Verzeichnis aktuell **kein** Git-Repository. Falls Versionskontrolle eingeführt wird, sollten `cycle_overlay/.venv/` und die großen generierten Dateien in `cycle_overlay/output/` (insbesondere `cycle_stats_full.parquet`, `*.html`, `*.json`) ausgeschlossen werden. |
| `requirements.txt` (oder `pyproject.toml`) | Fehlt; die `.venv` existiert nur lokal und ist nicht reproduzierbar dokumentiert. Empfehlung: `pip freeze > requirements.txt` aus dem vorhandenen `.venv` exportieren (mindestens `duckdb`, `pandas`, `numpy`, `pyarrow`, `plotly`). |
| `LICENSE` | Fehlt; für eine Abschlussarbeit ggf. nicht zwingend nötig, aber bei Weitergabe/Veröffentlichung des Codes empfehlenswert zu klären. |
| `tests/` | Keine automatisierten Tests vorhanden. Angesichts der Datenkritikalität (z. B. `loop_area()`, Bucket-Aggregation) wären zumindest einfache Unit-Tests für die reinen Berechnungsfunktionen (`loop_area`, `build_trend`) sinnvoll. |
| `.env.example` | Nicht anwendbar in aktueller Form, da Pfade/IDs hartkodiert sind – falls das Projekt wächst, wäre eine Auslagerung der Pfade/Signal-IDs in eine Konfigurationsdatei (z. B. `.env` oder `config.py`) sinnvoll, um Umgebungen zu wechseln, ohne Code zu ändern. |
| `docs/` | Nicht zwingend nötig, da `session-handoffs/` bereits als laufende Dokumentation dient; bei Wachstum könnte eine stabile `docs/`-Struktur (getrennt von den chronologischen Handoffs) sinnvoll werden. |

---

*Diese Dokumentation wurde automatisiert aus dem tatsächlichen Datei- und
Codebestand des Repositorys erstellt. Wo Herkunft oder Zweck einer Datei
nicht eindeutig aus dem Code ableitbar war, wurde dies explizit als
"nicht eindeutig erkennbar" bzw. "vermutlich" gekennzeichnet.*
