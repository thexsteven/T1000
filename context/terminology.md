# Terminology Glossary (German → English)

Authoritative German→English glossary for the T1000 thesis. All chapters must
use the **English** term on the right consistently. Derived from the context/
files (01–06). Where the training company's own naming is relevant it is noted.

| German (source term) | English (use this) | Notes |
|----------------------|--------------------|-------|
| Dauerlaufversuch / Dauerlauf | endurance test | avoid "continuous-run test"; keep "endurance test" throughout |
| elektrischer Linearaktuator | electric linear actuator | context also uses EN "electric rod-style actuator" |
| electric rodstyle actuator | rod-style electric actuator | company/source wording; introduce once, then "actuator" |
| Prüfstand | test rig | not "test bench" (stay consistent) |
| Prüfstandsversuch | test-rig trial / test run | |
| Prüfling | device under test (DUT) | context also: "test specimen"; prefer DUT after first mention |
| Testingenieur | test engineer | primary dashboard user |
| Versuchsserie | test series | company nomenclature, numbered consecutively |
| positionsgeregelt | position-controlled | |
| Bewegungstrajektorie | motion trajectory | |
| Bewegungszyklus / Zyklus | motion cycle / cycle | central analytical unit; "out-and-back" stroke |
| voller Hub | full stroke | |
| Ruhelage / Ruheposition | rest position | |
| Zyklusdauer | cycle duration | |
| Positionsspanne | position range (stroke) | |
| Zykluserkennung / Zyklus-Erkennung | cycle detection | pipeline stage 5 |
| Randzyklus (unvollständig) | (incomplete) boundary cycle | discarded during detection |
| Bewegungsschwellwert | motion threshold | provisional in existing pipeline |
| Schwellwert | threshold | |
| Aufzeichnungssitzung | recording session | pipeline splits at large time gaps |
| Aufzeichnungssitzungs-Erkennung | recording-session detection | pipeline stage 4 |
| Vorverarbeitungs-Pipeline | preprocessing pipeline | from the referenced master's thesis |
| hive-partitionierte Parquet-Dateien | hive-partitioned Parquet files | raw data format |
| Abtastrate | sampling rate | signals kept at native rate (no resampling) |
| Resampling / Interpolieren | resampling / interpolation | deliberately not applied |
| Multi-Sensor-Extraktion | multi-sensor extraction | pipeline stage 7 |
| Zyklus-Qualitätsprofilierung | cycle quality profiling | pipeline stage 8 (descriptive only) |
| Qualitätskennzahl / Qualitätsmetrik | quality metric | |
| Merkmal / Feature | feature | |
| Merkmalsvektor | feature vector | |
| Feature-Engineering | feature engineering | pipeline stage 9 (planned) |
| Merkmals-/Datensatz-Erzeugung | dataset generation | pipeline stage 10 (planned) |
| Datenqualität | data quality | central motivation |
| Entscheidungsbaum | decision tree | own contribution; four-level filter logic |
| Prüfebene / Ebene | (check) level | four levels of the decision tree |
| Datenpool | data pool | vetted subset of usable cycles |
| Datenpool-Ableitung | data pool derivation | own contribution |
| Pool nutzbarer Daten/Zyklen | pool of usable cycles | |
| Ablehnungsprotokoll | rejection log | documents why a cycle was excluded |
| Ablehnungsgrund | rejection reason | |
| Ablehnungsstatistik | rejection statistics | key empirical result |
| Reifegrad | maturity level | |
| Reifegradsystem | maturity-level system | five levels below |
| — inkonsistent | inconsistent | maturity level |
| — provisorisch | provisional | maturity level |
| — nicht begründet | unfounded | maturity level |
| — strukturell | structural | maturity level |
| — begründet | justified | maturity level |
| Stillstandserkennung | standstill detection | new level-2 check |
| Stillstand | standstill | |
| eingefrorenes Signal / Frozen-Signal | frozen signal | frozen sensor / stuck value |
| physikalische Plausibilitätsprüfung | physical plausibility check | missing gap in existing pipeline |
| Ausreißer(zyklus) | outlier (cycle) | |
| Mindestdauer-/Mindestbewegungsfilter | minimum-duration / minimum-motion filter | |
| Signalqualität | signal quality | level-4 check |
| Abdeckungsgrad | coverage (ratio) | temporal coverage within a cycle |
| Zeitlücke | time gap | |
| nicht endliche Werte | non-finite values | invalid signal values |
| Position | position | reference signal for cycle detection |
| Geschwindigkeit | velocity | extracted but unused in existing pipeline |
| Strom | current | |
| Druck | pressure | |
| Temperatur | temperature | |
| Vibration (x/y/z) | vibration (x/y/z) | highest sampling rate |
| Hysterese-/Kraftschleife | hysteresis / force loop | derived from current & position |
| Zustandsüberwachung | condition monitoring | data-driven target application |
| Restlebensdauer-Schätzung | remaining useful life (RUL) estimation | data-driven target application |
| datengetrieben | data-driven | thresholds derived from observed distributions |
| Zyklus-Overlay / HTML-Zyklus-Overlay | cycle overlay / HTML cycle overlay | own contribution (visualization) |
| Trend-Sicht | trend view | aggregated over full lifetime |
| Vergleichs-Sicht | comparison view | representative sampled cycles |
| Zeitabschnitt / Bucket | time segment / bucket | chronological aggregation unit |
| Perzentil | percentile | |
| repräsentative (Teil-)Stichprobe | representative (sub)sample | |
| Lifetime-Dashboard | lifetime dashboard | daily dashboard for test engineers |
| Verdichtung | aggregation / condensation | offline pre-aggregation before embedding |
| eigenständig lauffähige HTML-Datei | self-contained HTML file | no server / database at runtime |
| Masterarbeit | master's thesis | provides the preprocessing pipeline this work builds on |
| Praxissemester(-arbeit) | practical semester (thesis) | this T1000 project |

## Fixed phrasing decisions (keep consistent across chapters)

- "endurance test" (not "durability run", "continuous-run test").
- "test rig" (not "test bench").
- "motion cycle" on first mention, then "cycle".
- "data pool" (not "data set of usable cycles").
- "decision tree" refers to the manual, multi-level quality-check logic of this
  work — **not** a machine-learning decision-tree classifier. State this
  explicitly on first use to avoid confusion.
- "maturity level" for the five-way classification of how well a criterion is justified.
- "standstill detection" / "frozen signal" for the new level-2 check.
