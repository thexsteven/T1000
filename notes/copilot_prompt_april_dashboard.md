# Copilot-Prompt: April-Run (D63 Versuch1 / Nr 7) + Dashboard

> Kopiere alles unterhalb der Linie in Copilot.

---

## Rolle

Du arbeitest im Repo `~/t1000` auf `FLMC-AI` (SSH). Du baust einen reproduzierbaren
Pipeline-Run über den kompletten April 2026 für **D63 Versuch1** und daraus ein
funktionsfähiges, aber **bewusst ungestyltes** HTML-Dashboard. Das Styling macht
danach jemand anderes — investiere **null Zeit** in Optik.

## Vorab-Regel: erst verifizieren, dann bauen

Rate nichts. Bevor du Code schreibst, prüfe im Repo und berichte mir:

1. Wie wird `pipeline.py` aufgerufen? Welche CLI-Argumente / Config-Dateien
   (z. B. `example_pipeline_stage8.yaml`) steuern **Zeitraum**, **Versuch** und
   **Output-Verzeichnis**?
2. Wie funktioniert `extraction_checkpoint.json` — ist ein Resume nach Abbruch
   bereits möglich, oder muss ich das im Wrapper selbst lösen?
3. Welches Schema haben die Zyklus-Features? Sieh dir
   `outputs/D63_Nr7_8/Versuch1/20260720_080516/` an: `cycles/cycles.parquet`,
   `features/`, `quality_profiling/`, `sessions/sessions.csv`,
   `multi_sensor/measurements/batch_*.parquet`. Liste die Spalten der
   Feature-Tabelle auf.
4. Wo ist die Vier-Phasen-Zyklussegmentierung implementiert (Movement-Threshold
   aktuell `1.0`, maximal beobachtete untere Endlage `0.992`)? Ich will diese
   Logik **wiederverwenden**, nicht neu erfinden.
5. Ist `Versuch1` tatsächlich Prüfling **Nr 7**? Verifiziere gegen Doku/Metadaten.

Danach: **kurzer Plan (max. 20 Zeilen) mit deinen Annahmen an mich, bevor du
loslegst.** Alles, was du nicht verifizieren konntest, kommt in eine
`ASSUMPTIONS.md` — nicht stillschweigend in den Code.

## Kontext: Anlage & Signale

Prüfstandsparameter (aus `Lifetime_report_endurance_test.xlsx`, Blatt `D63_Nr_7_8_9`):

- `cycletime = 5.65 s`, `real stroke = 380 mm`
- daraus erwartet: **≈ 637 Zyklen/h**, **≈ 15.300 Zyklen/Tag**, **≈ 460.000 Zyklen im April**

Signale für Versuch1 (aus `metadata/uuid_signal_catalogue.csv`):

| Quelle | Signal | Einheit |
|---|---|---|
| Drive | current | A |
| Drive | position | m |
| Drive | velocity | m/s |
| ESP32 | counter | integer |
| ESP32 | vibration X / Y / Z | m/s² |
| Messrack | pressure | Pa |
| Wago | counter | integer |
| Wago | temperature Motor | °C |
| Wago | temperature fixed_bearing_actuator | °C |
| Wago | temperature spindle_nut | °C |

## Zeitraum

- **Hauptfenster:** 2026-04-01 00:00 bis 2026-04-30 23:59
- **Baseline-Vorlauf:** zusätzlich ab 2026-03-25 mitziehen, im Dashboard aber
  klar als „vor April" gekennzeichnet
- Zeitzone explizit festlegen (Anlagenzeit) und in den Metadaten dokumentieren.
  Achte auf die DST-Umstellung am 29.03.2026.

**Warum dieser Monat wichtig ist:** am 26.05.2026 steht im Versuchslog „Stopp
aller Versuche (Lebensdauerende Nr 7 und 8)". Der April ist damit das Fenster
**4–8 Wochen vor Lebensdauerende** — Degradation soll hier sichtbar werden.

## Eingriffs-Log (fest hinterlegen)

Lege eine `config/events_d63_versuch1.json` mit genau diesen Einträgen an. Sie
werden im Dashboard als vertikale Marker über allen Zeitreihen gezeichnet und
sind der Schlüssel dafür, Eingriffe nicht als Anomalien fehlzudeuten.

```json
[
  {"ts_start":"2026-03-30T14:34:00","ts_end":null,"type":"parameter_change","scope":"Versuch1","label":"Weg +0,2 mm bei Nr 7 (max. Druck erreichen)"},
  {"ts_start":"2026-04-02T07:13:00","ts_end":null,"type":"sync","scope":"all","label":"Sync"},
  {"ts_start":"2026-04-08T07:11:00","ts_end":"2026-04-08T07:34:00","type":"maintenance_stop","scope":"all","label":"Stopp aller Versuche, Nachschmieren Antrieb Nr 9"},
  {"ts_start":"2026-04-17T09:28:00","ts_end":null,"type":"sync","scope":"all","label":"Sync"},
  {"ts_start":"2026-04-24T07:30:00","ts_end":null,"type":"sync","scope":"all","label":"Sync"},
  {"ts_start":"2026-04-30T13:39:00","ts_end":null,"type":"sync","scope":"all","label":"Sync"}
]
```

Kontext außerhalb des Fensters (nur als Notiz im README, nicht als Marker):
23.03. Regreasing Nr 7, 27.03. Regreasing Nr 8, 26.05. Lebensdauerende Nr 7/8 + Ausfall Nr 9.

---

## Aufgabe 1 — Pipeline-Run über den April

Schreibe `scripts/run_april_2026.py` als **Wrapper** um `pipeline.py`.
**`pipeline.py` selbst nicht verändern.**

Anforderungen:

- **Tageweise Chunks.** Ein Monolith-Run über 30 Tage bricht irgendwann ab und
  fängt sonst von vorn an.
- **Resumebar.** Bereits fertige Tage werden übersprungen (eigene
  `run_state.json` mit Status pro Tag: `pending | running | done | failed`).
- **Fehlertoleranz.** Ein fehlgeschlagener Tag stoppt nicht den Rest; er wird
  als `failed` markiert, mit Traceback ins Log, und am Ende zusammengefasst.
- **Logging** pro Tag in `logs/april_2026/<YYYY-MM-DD>.log`, plus ein
  Gesamt-Log mit Laufzeit und Zyklenzahl je Tag.
- **Output** nach `outputs/D63_Nr7_8/Versuch1/april_2026_<YYYYMMDD_HHMMSS>/`,
  Struktur analog zu bestehenden Runs.
- **Run-Manifest** `run_manifest.json`: Git-Commit, Config-Hash, Zeitraum,
  Start-/Endzeit, verarbeitete Tage, Zyklenzahl, Warnungen.

**Reihenfolge — wichtig:**

1. Erst ein **Testlauf über einen einzigen Tag** (nimm **2026-04-03**, ein Tag
   ohne dokumentierten Eingriff).
2. Danach berichtest du mir: Laufzeit, Peak-RAM, Output-Größe auf Platte,
   Zyklenzahl, Spalten der Feature-Tabelle — und die **hochgerechnete
   Gesamtlaufzeit und Plattenbelegung für 30 Tage**.
3. **Warte auf mein Go**, bevor du den vollen Monat startest.

Wenn die Hochrechnung Plattenplatz oder Laufzeit sprengt: sag es mir mit
konkreten Zahlen und schlage eine Reduktion vor (z. B. Rohdaten nach der
Feature-Extraktion je Tag verwerfen), statt es einfach zu tun.

---

## Aufgabe 2 — Aggregation zu `dashboard_data.json`

Schreibe `scripts/build_dashboard_data.py`.

**Parametrisiert** über `--run-dir`, `--date-from`, `--date-to`, `--events`,
`--out` — das Skript soll später auch für andere Versuche und Monate
funktionieren, nicht nur für diesen einen Fall.

**Input:** die Zyklus-Features aus dem April-Run.
**Output:** **eine einzige** `dashboard_data.json`, **Zielgröße < 8 MB**.

Rohsignale kommen niemals ins JSON. Vier Ebenen:

### Ebene A — Stundenaggregate (~816 Zeilen inkl. Vorlauf)

Pro Stunde und pro Metrik: `n`, `mean`, `p05`, `p50`, `p95`, `max`, `std`.

Metriken:

- `drive_current`: mean, RMS, peak — **gesamt und je Zyklusphase 1–4**
- `vibration_rms` X, Y, Z und Resultierende — **je Phase**
- `temp_motor`, `temp_fixed_bearing`, `temp_spindle_nut` sowie die Deltas
  `spindle_nut − motor` und `fixed_bearing − motor`
  (Deltas sind robuster gegen Hallentemperatur-Schwankungen als Absolutwerte)
- `pressure`: mean, p95 — dient als **Last-Kovariate**, nicht als Verschleißmaß
- `cycle_time_actual`: median, std
- `position_end_upper`, `position_end_lower` je Zyklus → Median + Drift
  (die untere Endlage relativ zum Movement-Threshold ist ein direktes
  Verschleißsignal — bitte mit aufnehmen)
- `velocity_max` je Phase

### Ebene B — Tagesaggregate + Trendstatistik (30 Zeilen)

- dieselben Metriken als Tagesmedian + IQR
- rollierender 24-h-Median als geglättete Trendlinie
- pro Metrik eine **lineare Regression über das Monatsfenster**:
  `slope` (Einheit/Tag), `r2`, `p_value`, `pct_change_over_month`
- daraus eine sortierbare **Ranking-Tabelle „stärkste Veränderung im April"**
- Regression **ohne** die Stunden rechnen, die von einem Event betroffen sind
  (± 1 h um Sync, gesamtes Stopp-Intervall am 08.04.), und das im JSON
  vermerken (`excluded_hours`)

### Ebene C — Coverage & Datenqualität (stündlich)

- `expected_cycles = 3600 / 5.65 ≈ 637`, `actual_cycles`, `coverage_pct`
- pro Signal: NaN-Rate, Anteil konstanter/eingefrorener Werte
  (Sensor-Hänger sind in dieser Anlage historisch vorgekommen)
- **Lückenliste**: alle Unterbrechungen > 5 min mit Start, Ende, Dauer,
  betroffenen Signalen und — falls zeitlich passend — dem zugeordneten Event
- Kennzeichnung, welche Stunden durch ein Event erklärt sind und welche **nicht**
  (die unerklärten sind das eigentlich Interessante)

### Ebene D — Zyklus-Stichprobe für den Drill-down (max. 120 Zyklen)

- 1 Median-Zyklus pro Tag (30)
- 1 Zyklus mit p95-Strom pro Tag (30)
- je bis zu 10 Zyklen unmittelbar vor und nach jedem Event
- bis zu 20 Anomalie-Kandidaten (größte Abweichung vom rollierenden Baseline-Median)

Pro Zyklus nur: `position`, `current`, `velocity`, `vibration_resultant`,
jeweils auf **max. 400 Punkte downgesampelt**, plus die vier Phasengrenzen und
ein `selection_reason`-Feld.

### JSON-Format

- `schema_version: "1.0"` und ein `meta`-Block: Run-ID, Zeitraum, Zeitzone,
  Erzeugungszeitpunkt, Quellpfade, Git-Commit, **Einheiten pro Metrik**
- Floats auf 4 signifikante Stellen runden — das allein spart massiv Größe
- Am Ende die tatsächliche Dateigröße ausgeben. Bei > 8 MB: **Zyklen-Stichprobe
  reduzieren**, nicht die Aggregate ausdünnen.

---

## Aufgabe 3 — HTML-Dashboard (bewusst roh)

Eine Datei: `dashboard_april_2026.html`.

**Harte Anforderungen:**

- **Standalone**, muss per Doppelklick über `file://` funktionieren
- JSON eingebettet als `<script type="application/json" id="dashboard-data">…</script>`
- **Kein CDN, kein Build-Step, kein npm.** Falls du eine Chart-Library nutzt,
  muss sie vollständig inline eingebettet sein — empfohlen **uPlot** (~40 KB,
  performant bei vielen Punkten). Alternativ reines Canvas/SVG.
- Läuft flüssig mit ~800 Stundenpunkten × ~25 Metriken

**Drei Tabs:**

**1. Trends**
- Zeitreihen-Charts (Stunde/Tag umschaltbar) pro Metrikgruppe: Strom,
  Vibration, Temperatur, Zykluszeit, Endlagen
- Event-Marker als vertikale Linien mit Tooltip-Label über allen Charts
- Baseline-Vorlauf visuell abgesetzt vom April
- Ranking-Tabelle „stärkste Veränderung" mit slope, %-Änderung, r², p
- Umschalter „je Phase" / „gesamt"

**2. Qualität & Coverage**
- Coverage-Heatmap Tag × Stunde (30 × 24)
- Lückentabelle, sortierbar, mit Spalte „durch Event erklärt: ja/nein"
- Balken NaN-Rate und Freeze-Rate pro Signal
- Kennzahlenzeile oben: Gesamt-Coverage %, Zyklen gesamt, Anzahl Lücken,
  längste Lücke

**3. Zyklus-Detail**
- Liste/Dropdown der ~120 Stichprobenzyklen, gefiltert nach `selection_reason`
- Ausgewählter Zyklus: Overlay-Plot position/current/velocity/vibration über
  die Zyklusdauer, die vier Phasen farblich hinterlegt
- Vergleichsmodus: zwei Zyklen übereinander (z. B. 01.04. vs. 30.04.)

**Zum Code-Stil — das ist wichtig, weil das HTML danach umgestaltet wird:**

- **Kein Design.** Kein CSS-Framework, keine Farbpaletten, keine Icons, keine
  Animationen. Ungestylte Buttons und Tabellen sind ausdrücklich richtig.
- Gesamtes CSS in **einem** `<style>`-Block oben. **Keine** `style=`-Attribute
  im Markup, keine im JS gesetzten Farben/Größen — sonst lässt sich das Styling
  später nicht sauber ersetzen.
- Semantisches HTML, stabile `id`- und `data-*`-Attribute an allen Containern.
- Gesamte Logik in einem `<script>` unten, in klar benannten Funktionen
  (`renderTrends()`, `renderCoverage()`, `renderCycleDetail()`), mit Kommentaren.
- Datenzugriff über eine schmale Schicht (`getMetric(name, resolution)`), damit
  Render-Code und JSON-Struktur nicht verklebt sind.

---

## Aufgabe 4 — Doku

- `README_april_run.md`: wie der Run gestartet wurde, tatsächliche Laufzeit,
  getroffene Entscheidungen, bekannte Lücken und deren Ursache, wie man das
  Ganze für einen anderen Versuch/Monat wiederholt
- `docs/dashboard_data_schema.md`: Feld-für-Feld-Beschreibung des JSON inkl. Einheiten
- `ASSUMPTIONS.md`: alles, was du nicht verifizieren konntest

---

## Akzeptanzkriterien

- [ ] Testlauf 2026-04-03 erfolgreich, Hochrechnung an mich berichtet, Go abgewartet
- [ ] Voller April-Run abgeschlossen, `run_state.json` zeigt für jeden Tag `done` oder begründetes `failed`
- [ ] Nach künstlichem Abbruch setzt ein Neustart korrekt am nächsten offenen Tag auf
- [ ] `dashboard_data.json` < 8 MB, valides JSON, `schema_version` und `meta` vorhanden
- [ ] Summe `n_cycles` über alle Stunden stimmt mit der Zyklenzahl aus dem Run-Manifest überein
- [ ] Alle 6 Events erscheinen als Marker in allen Trend-Charts
- [ ] HTML öffnet per `file://` ohne Konsolenfehler und ohne Netzwerkzugriff
- [ ] Alle drei Tabs rendern mit echten Daten, kein Platzhalter
- [ ] `build_dashboard_data.py` läuft mit anderen `--run-dir`/`--date-from`-Werten durch

## Was du NICHT tun sollst

- Kein Styling, keine Politur, keine Farbschemata
- `pipeline.py` nicht verändern
- Keine Werte erfinden, keine Platzhalterdaten, keine Mock-Charts
- Nicht über Datenlücken hinweg interpolieren — Lücken bleiben Lücken
- Keine stillen Annahmen: alles Unklare kommt in `ASSUMPTIONS.md` und wird mir gemeldet
