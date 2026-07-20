# Analyse: Kriterien für den "Pool nutzbarer Daten" im MasterThesis-Repository

Analysiertes Quell-Repository: `/home/ita/MasterThesis`
Autorin des analysierten Thesis-Codes: Fatemeh Heydari

**Hinweis:** Es existiert kein repository-weiter Begriff "standstill" (Stillstand). Es handelt
sich um eine Vorverarbeitungs-/Zyklus-Extraktions-Pipeline (noch kein ML-"Usefulness"-Klassifikator),
verfasst von Fatemeh Heydari. Im Folgenden die evidenzbasierte Aufschlüsselung, gegliedert nach
den 5 angeforderten Punkten.

---

## 1. Filterkriterien (alle gefundenen "Usefulness"-/Gültigkeits-Logiken)

| Kriterium | Ort | Logik |
|---|---|---|
| **Bewegungsschwellwert (Zyklusgrenze)** | `src/preprocessing/cycle_detection.py:56,74` `detect_candidate_cycles()` | Position `value > 1.0` (Standardwert `movement_threshold`) = "in Bewegung"; ein Zyklus beginnt beim Übergang `<=1.0 → >1.0`, endet bei `>1.0 → <=1.0`. Unvollständige Randzyklen werden verworfen (Zeilen 60-63, 91-92). |
| **Aufzeichnungssitzungs-Lücke** | `src/preprocessing/session_detection.py:28,140` | `DEFAULT_SESSION_GAP_SECONDS = 3600.0` (1 Std.). Eine Zeitstempel-Lücke `> Schwellwert` startet eine neue Sitzung; verhindert Zyklus-Erkennung über Aufzeichnungsunterbrechungen hinweg. |
| **Multi-Sensor-Validierungsbereitschaft** | `src/preprocessing/validation_cycle_selection.py:38-89` `_evaluate_cycle_quality()` | Ein Zyklus ist nur `is_validation_ready`, wenn jeder Eintrag in `required_signals` existiert (nicht leer) UND `>= minimum_samples[signal]` Zeilen hat (konfiguriert in `configs/example_pipeline.yaml:41-49`, z. B. Position/Geschwindigkeit/Strom/Vibration ≥20 Samples, Druck/Temperatur ≥1). |
| **Auswahl zusammenhängender Blöcke** | `validation_cycle_selection.py:101,166-186` | `require_consecutive=True` setzt den Kandidatenblock bei jedem fehlgeschlagenen Zyklus zurück — nur lückenlos aufeinanderfolgende "gute" Zyklen (gleiche Sitzung) werden für die Validierungs-Teilmenge akzeptiert. |
| **Genau-ein-Signal-Plausibilitätsprüfung** | `scripts/analyze_position_cycles.py:49-52`, `src/analysis/analyze_dataset.py:212-215` | Experimente werden übersprungen bzw. lösen einen Fehler aus, wenn `len(position_signals) != 1`. |
| **Verwerfen fehlender/ungültiger Zeilen** | `cycle_detection.py:39-45` `_prepare_position_frame()` | Zeilen mit NaN bei `time`/`value` werden vor der Erkennung verworfen (protokolliert, nicht stillschweigend beibehalten). |

---

## 2. Stillstandserkennung

Es existiert kein dediziertes "Stillstand"-Konzept (kein Fenster-Detektor für
Geschwindigkeit-nahe-null, keine explizite Kennzeichnung von Ruhephasen). Der einzige verwandte
Mechanismus ist die **binäre Bewegt/Nicht-bewegt-Klassifikation innerhalb von
`detect_candidate_cycles`** (`cycle_detection.py:74`,
`is_moving = prepared_df["value"] > movement_threshold`). Diese dient ausschließlich der
Bestimmung von Zyklus-Start-/Endpunkten auf dem Positionssignal, nicht der Charakterisierung
oder Herausfilterung von Stillstandsabschnitten als "unbrauchbar". Geschwindigkeits- und
Stromsignale existieren und werden extrahiert (`multi_sensor_cycle_extraction.py`), werden aber
nie für eine Stillstands-/Ruhezustandserkennung verwendet.

---

## 3. Begründung je Kriterium

- **Bewegungsschwellwert = 1.0**: Nirgends numerisch begründet. Explizit als vorläufig
  gekennzeichnet: `scripts/analyze_position_cycles.py:23-25` — *"Temporary exploratory
  threshold that must be validated from the observed cycle statistics and annotated plots
  before it becomes a final rule."* (Temporärer, explorativer Schwellwert, der anhand der
  beobachteten Zyklusstatistiken und annotierten Plots validiert werden muss, bevor er zu
  einer endgültigen Regel wird.) Derselbe Wert wiederholt sich in
  `scripts/analyze_multi_sensor_cycle.py:32` und `configs/example_pipeline.yaml:6` ohne
  Herleitung.
- **Position als Referenzsignal für Zyklen**: Begründet durch fachliche Vorgabe der
  Betreuenden — ADR-007 in `docs/architecture_decisions.md` (Zeilen 374-413) und
  `docs/thesis_pipeline.md:295-303`: *"the electrical actuator is position-controlled and
  follows a predefined position trajectory."* (Der elektrische Aktuator ist positionsgeregelt
  und folgt einer vorgegebenen Positionstrajektorie.)
- **1-Stunden-Schwellwert für Sitzungslücken**: Ebenfalls als explorativ gekennzeichnet —
  `scripts/analyze_recording_sessions.py:20-21` — *"This 1 hour gap threshold is exploratory
  and must be validated using the resulting session statistics before it is treated as a
  final rule."* (Dieser 1-Stunden-Lückenschwellwert ist explorativ und muss anhand der
  resultierenden Sitzungsstatistiken validiert werden, bevor er als endgültige Regel gilt.)
  ADR-006 (`architecture_decisions.md:341-370`) behauptet, er sei "based on the empirical
  timestamp analysis" (auf der empirischen Zeitstempelanalyse basierend), aber im ADR selbst
  wird kein Analyse-Output bzw. keine Schwellwert-Herleitungszahl gezeigt.
- **Keine Interpolation/kein Resampling ("native sampling")**: ADR-008
  (`architecture_decisions.md:416-464`) — Entscheidung, native Zeitstempel statt Resampling
  zu erhalten, begründet nur mit unterschiedlichen Sample-Zahlen je Sensor, bislang nicht
  gegen die Anforderungen des Feature-Engineerings getestet.
- **Mindest-Sample-Anzahlen je Signal (20 vs. 1)**: `configs/example_pipeline.yaml:41-49` —
  kein Kommentar/keine Begründung, warum Position/Geschwindigkeit/Strom/Vibration ≥20, aber
  Druck/Temperatur nur ≥1 benötigen (spiegelt vermutlich deren geringere native Abtastrate
  wider, vermerkt in `implementation_log.md:332-352`, aber dieser Zusammenhang wird nirgends
  explizit im Code oder in der Dokumentation genannt).

---

## 4. Lücken & Unklarheiten

- **`movement_threshold=1.0`** ist eine an 3 Stellen duplizierte Magic Number
  (Standardwert in `cycle_detection.py`, `analyze_position_cycles.py`,
  `analyze_multi_sensor_cycle.py`, `example_pipeline.yaml`) ohne jegliche
  Einheiten-/physikalische Begründung (die Positionseinheit wird nicht genannt — vermutlich
  mm o. Ä.) und explizit als "temporär" markiert.
- **Sitzungslücke = 3600 s** ist ebenfalls explizit als explorativ markiert, ist aber bereits
  der hartcodierte Standardwert in den Produktionsstufen (`pipeline.py`, `analyze_dataset.py`)
  — d. h. ein unvalidierter Schwellwert hat sich in die "akzeptierte" Pipeline fortgepflanzt
  (ADR-006 markiert ihn als "Accepted", während der Skript-Kommentar ihn "exploratory" nennt —
  Widerspruch zwischen ADR-Status und Formulierung im Skript).
- **Kein "Usefulness"-Score für Zyklen über die strukturelle Vollständigkeit hinaus** — ein
  Zyklus wird aktuell nur nach *Signalvorhandensein/Sample-Anzahl* als "bereit" beurteilt
  (`validation_cycle_selection.py`), nicht nach physikalischer Plausibilität (z. B. ändert
  sich die Position tatsächlich, liegt die Dauer in einem sinnvollen Bereich, gibt es
  Sensorsättigung/Ausreißerwerte). Zyklusdauer-/Positionsspannen-Statistiken werden berechnet
  (Spalten in `cycle_detection.py`), aber nie als Filter verwendet — sie sind rein
  beschreibend.
- **Stillstands-/Ruhephasen werden nicht von gültigen kurzen Zyklen unterschieden** — ein
  "Zyklus" von nur einem einzigen Sample oberhalb des Schwellwerts würde akzeptiert; es
  existiert kein Mindestdauer- oder Mindestverschiebungsfilter.
- **Die Stufe "Signal Quality Assessment" ist "In Progress"/undefiniert** —
  `docs/thesis_pipeline.md:366-384` (Stufe 8) listet vorgesehene Prüfungen (fehlende Kanäle,
  Zeitstempel-Konsistenz, Abtastverhalten) auf, aber es existiert noch keine Implementierung
  in `src/` für diese Stufe über die Sample-Anzahl-Prüfung der Validierungsauswahl hinaus.
- **Inkonsistente Einheiten-/Schwellwertsemantik**: `movement_threshold` vergleicht den
  rohen Positionswert mit einer absoluten Zahl, ohne Bezug zum dynamischen Wertebereich des
  Signals (`implementation_log.md` berichtet einen Positions-Peak von ≈85), sodass
  "bewegt" vs. "nicht bewegt" ein fixer, willkürlich gewählter Grenzwert bei ~1 % des
  typischen Peaks ist.

---

## 5. Verbesserungsvorschläge

Besonderer Fokus auf das Problem "laufende" vs. "stillstehende" Daten:

- **Stillstand explizit über ein Fensterkriterium definieren**, nicht nur über einen
  statischen Positionsschwellwert: z. B. über ein gleitendes Fenster von *N* Samples oder
  *T* Sekunden, Stillstand = `max(position) - min(position) < Δ_pos` UND/ODER
  `|velocity| < ε_v` für das gesamte Fenster. Dies adressiert direkt "Positionswerte bleiben
  konstant" und ist robuster als ein einzelner Schwellwert-Übergang auf Basis eines einzelnen
  Samples.
- **Geschwindigkeit (bereits extrahiert) als bestätigendes Signal nutzen**, statt sich
  ausschließlich auf Position zu verlassen — ein positionsbasierter Schwellwert vermischt
  "kleine Bewegung" mit "keine Bewegung"; Geschwindigkeit nahe null ist ein direkterer
  physikalischer Indikator für Stillstand und wird bereits pro Zyklus geladen
  (`multi_sensor_cycle_extraction.py`), nur bislang nicht zu diesem Zweck genutzt.
- **Einen Mindestdauer-/Mindestverschiebungsfilter** zu `detect_candidate_cycles` hinzufügen,
  damit trivial kurze "Zyklen" (Rauschen, das den Schwellwert überschreitet) abgelehnt
  werden — aktuell werden Dauer/Positionsspanne berechnet, aber nicht durchgesetzt
  (`cycle_detection.py:106-110`).
- **Die beiden "explorativen" Schwellwerte (`movement_threshold`, Sitzungslücke) anhand der
  bereits verfügbaren zugrunde liegenden Verteilungen validieren** — `time_gap_analysis.py`
  berechnet Lücken-Perzentile; `movement_threshold` könnte analog aus dem Rauschgrund des
  Positionssignals im Ruhezustand abgeleitet werden (z. B. perzentilbasiert, statt fix bei
  1.0).
- **ADR-Status mit Code-Kommentaren abgleichen**: ADR-006 sagt "Accepted" für die
  1-Stunden-Lücke, während das Skript sie weiterhin "exploratory" nennt — eine
  einheitliche Quelle der Wahrheit festlegen und die empirische Grundlage dokumentieren
  (z. B. das tatsächliche Lücken-Histogramm/die zitierten Perzentilzahlen anfügen).
- **Signal Quality Assessment (Stufe 8) zu einem konkreten Filter ausbauen**, der
  kombiniert: Ausreichende Sample-Anzahl (bereits vorhanden), Plausibilität des
  Signalwertebereichs (z. B. Zyklen ablehnen, bei denen Position `movement_threshold` nie
  nennenswert überschreitet — ein Reststillstandsartefakt), und Dauergrenzen, abgeleitet aus
  der berichteten typischen Zyklusdauer (~3,1 s, `implementation_log.md:279-281`), um
  Ausreißerzyklen als Kandidaten für den Ausschluss aus dem "nutzbaren Pool" zu markieren.
