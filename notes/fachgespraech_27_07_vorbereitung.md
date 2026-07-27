# Fachgespräch 27.07.2026 — Vorbereitung

## Was ich zeige

Dashboard `d63_interactive_dashboard.html` (D63 / Versuch1, 60.901 Zyklen,
Block 14.08.–18.08.2025) — offline lauffähig, kein Netz nötig.

Dazu Sandros Anfrage aus dem letzten Meeting: **100 Zyklen, Position und
Motorstrom überlagert, X-Achse Zeit, zwei Y-Achsen.** Vor dem Termin prüfen,
ob der Tab "Cycle Comparison" das bereits liefert — falls dort nur Position
liegt, ist das der einzige echte Nachrüstpunkt.

---

## Torbens Fragen, die ich aus den Daten beantworte

| Frage | Meine Auswertung | Beleg |
|---|---|---|
| **2.1** Positionssignal im Stillstand, Auflösung | σ im Stillstandsfenster + sichtbare Quantisierungsstufen | `standstill_noise_histogram` |
| **3.1** Zyklusdefinition (Hin/Rück mit Haltezeit?) | Periode 5,65 s = **3,737 s Bewegung + 1,910 s Halt**, Einzelhub ≈ 1,87 s | `cycle_duration_histogram` |
| **3.3** Streuung der Zyklusdauer | Verteilung p1/p99 → daraus Akzeptanzband | `cycle_duration_histogram` |
| **4.1** Abtastrate | Δt je Kanal, nominale Rate + Jitter | offen: 20 Hz bisher behauptet, nicht belegt |
| **4.2** Aufzeichnungslücken | **Drei Regime statt zwei**: normale Abtastung, Zwischenband 1,507–20,134 s, lange Sessionpause | `gap_distribution_histogram` |
| **1.1** Endlagen / Hub | beobachtete Streuung der Endlagen | `position_endstops_histogram` |

**Wichtigster Fund für den Termin:** Torben schreibt zu 4.2, systembedingte
Lücken seien *nicht bewusst programmiert*. In den Daten existiert aber ein
Zwischenband von 1,507–20,134 s. Das ist erklärungsbedürftig und mein aktueller
3600-s-Schwellenwert erfasst es nicht (Status: `Inkonsistent`).

---

## Was Torbens Antworten für meine Kriterien bedeuten

**Position ist das Referenzsignal.** Zu 5.2: Die Regelung ist positionsgeregelt —
verändert sich der Positionsverlauf nicht wesentlich, ist der Zyklus normal
verfahren. Damit ist meine physikalische Plausibilitätsprüfung *am Positionssignal*
sachlich begründet und nicht nur eine Konvention.

**Haltezeit ist fest programmiert** (3.2). Meine gemessenen 1,910 s sind damit ein
Sollwert, kein Streuwert — starke Abweichungen sind ein Fehlerindikator.

**Der Regler stoppt bei Überschreitung der Bewegungsgrenzen** (3.3). Extreme
Zyklusdauern dürften also gar nicht auftreten. Das begrenzt mein Akzeptanzband
nach oben physikalisch.

**Positions-Offset ist erwartbar** (1.1): Der SRTA fährt nicht in den mechanischen
Anschlag; der Pneumatikzylinder kann ihn hinter die Soll-Nullposition drücken.
Das erklärt Streuung an der unteren Endlage — kein Messfehler.

**Motorstrom hat keine Sollreferenz** (1.2). Auffälligkeiten nur relativ:
steigende Spitzen, zunehmende Schwingungen, steigender RMS.

---

## Was ich nachfragen muss

1. **Geschwindigkeitsskalierung** (2.2) — Torben kennt die Rohdaten-Einheit nicht
   und verweist aufs Grafana-Dashboard. Wer kann die Skalierung bestätigen?
   Bis dahin bleiben meine Werte (~62.978) als *raw counts* gekennzeichnet.
2. **Programmänderungen** (3.4) — Torben hat Alexander Hahn adressiert:
   Reglerparameter wurden angepasst, Bewegungsprofil nicht. Wann genau?
   Ein Parameterwechsel mitten im Aufzeichnungszeitraum verschiebt meine
   Referenzpopulation.
3. **Event-Log** (4.3 / 5.3) — geplante Stopps für Wartung und Synchronisation
   sind dokumentiert, aber „wahrscheinlich nicht zu 100 %". Kann ich das Log
   gegen meine detektierten Blockgrenzen abgleichen?
4. **Movement Threshold**: aktuell `Position > 1.0`, Status `Nicht begründet`.
   Vorschlag: aus der gemessenen Stillstands-σ ableiten (z. B. Vielfaches von σ)
   statt Festwert. Ist das aus Reglersicht sinnvoll?

---

## Haltung im Gespräch

Nicht „hier sind fertige Schwellenwerte", sondern: *für zwei Kriterien stützt die
Verteilung den aktuellen Wert nicht.* Alle gezeigten Schwellen sind provisorisch.
Verworfene Zyklen werden nie gelöscht — sie bekommen ein `rejection_reason`,
die Rohdaten bleiben unangetastet, der Pool ist nur ein Index.
