# Präsentationsleitfaden: Actuator Lifetime Dashboard für D32 / Versuch1

Dieser Leitfaden hilft dir, den Aufbau, Zweck und Wert des Dashboards auf
Deutsch zu erklären. Er ist so strukturiert, dass du
- den technischen Ablauf beschreiben kannst,
- die wichtigsten Vorteile hervorhebst,
- häufige Fragen der Betreuer beantworten kannst,
- und mögliche Kritikpunkte sachlich einordnest.

---

## 1. Kernbotschaft

Das Dashboard ist ein **einzelnes, selbstständiges HTML-Dokument**, das
ohne Server läuft und trotzdem Erkenntnisse aus einem sehr großen
datentechnischen Rohsatz liefert:
- 8,658,098 Zyklusbeobachtungen insgesamt,
- 7,690,500 davon als "aktive" Testzyklen,
- mehr als 6 Monate Betriebszeit abgedeckt.

Wichtig: Es nutzt einen **offline-Preprocessing-Workflow**, um die Daten
auf zwei sinnvolle Ebenen zu reduzieren:
1. eine Trend-Übersicht über den gesamten Testverlauf,
2. eine detaillierte Detailansicht für eine repräsentative Stichprobe
   einzelner Zyklen.

Diese Trennung ist die zentrale Stärke: Sie erhält die Aussagekraft des
Gesamttests, ohne den Browser zu überladen.

---

## 2. So funktioniert der Build-Prozess

### 2.1. Stufe 1: Signal-Daten werden zu Zyklusstatistiken

Das Skript `extract_cycle_stats.py` liest die Rohdaten aus den
Parquet-Dateien und berechnet für jeden einzelnen der 8,66 Mio. Zyklen
aggregate Kenngrößen:
- Dauer,
- Peak-Werte,
- Mittelwerte,
- Min/Max,
- Aktivitätsstatus.

Diese Aggregation passiert mit **DuckDB** und einer ASOF-Join-Technik,
so dass nicht alle Rohdaten gleichzeitig in den Speicher geladen werden.
Ergebnis: `cycle_stats_full.parquet` mit einer Zeile pro Zyklus.

### 2.2. Stufe 2: Dashboard-Daten vorbereiten

Das Skript `build_dashboard_data.py` erzeugt daraus zwei kompakte
Artefakte:
- `trend.json`: 3.000 zeitlich gleich große Buckets über alle aktiven
  Zyklen, jeweils mit Mittelwert, 10. und 90. Perzentil pro Kennzahl.
- `pool.json`: 1.500 repräsentativ über die Zeit verteilte Zyklen mit
  vollständigen Wellenformen für relevante Signale.
- `meta.json`: Metadaten wie Start-/Endzeit, Zyklus-Anzahl, Pool-Größe.

### 2.3. Stufe 3: HTML erzeugen

`build_html.py` nimmt die Vorlagen-HTML und ersetzt Platzhalter mit den
kompakten JSON-Daten. Das Resultat ist ein fertiges Dashboard-HTML,
welches die Daten direkt als JavaScript-Variablen ins Dokument einbettet.

---

## 3. Was das Dashboard zeigt

### Überblicksseite

- Statistikkarten für Testdauer, Anzahl aktiver Zyklen, Spitzenwerte,
  Durchschnittsdrücke, Temperaturen und Zyklusdauer.
- Eine Zeitreihen-Visualisierung des Testverlaufs mit auswählbaren
  Kennzahlen.
- Bei mehreren ausgewählten Kennzahlen werden die Kurven so skaliert,
  dass sie vergleichbar bleiben, aber die Werte im Tooltip weiterhin in
  den Originaleinheiten angezeigt werden.

### Vergleichsansicht

- Auswahl einzelner Zyklen per ID, zufälliger Stichprobe oder Referenzzyklus.
- Überlagerte Wellenformen für Geschwindigkeit, Position, Strom,
  Druck und Temperatur.
- Eine Vergleichstabelle mit abgeleiteten Kenngrößen wie Hub, Peak-Speed,
  Peak-Strom und Abweichungen zum Referenzzyklus.

---

## 4. Warum dieser Ansatz sinnvoll ist

### Stärke 1: Skalierbarkeit

Die Rohdaten umfassen mehrere Hundert Millionen Einzelmessungen.
Ohne Vorverarbeitung wäre ein Browser-Dashboard nicht realistisch. Der
Ansatz reduziert die Daten systematisch, bevor sie ins Frontend kommen.

### Stärke 2: Transparenz

- Der Trend basiert auf **allen aktiven Zyklen**, nicht nur einer Probe.
- Die Vergleichsansicht ist klar als **repräsentative Stichprobe**
  ausgewiesen.
- Die eingesetzten Metriken bleiben in den Originaleinheiten
  (m/s, m, A, Pa, °C).

### Stärke 3: Portable Verwendbarkeit

Das finale HTML ist eine unabhängige Datei. Es kann mit einem Doppelklick
geöffnet werden, ohne Webserver, Datenbank oder spezielle Infrastruktur.

---

## 5. Kritische Punkte, die du erklären kannst

### Schwachpunkt 1: Stichprobe ist begrenzt

Die Vergleichsansicht zeigt nur 1.500 von 8,66 Mio. Zyklen. Das ist ein
bewusster Kompromiss, um die Datei handhabbar zu halten. Die Auswahl ist
gleichmäßig über die Testdauer verteilt, aber sie deckt nicht jeden
Einzelzyklus ab.

### Schwachpunkt 2: Keine automatische Anomalieerkennung

Der aktuelle Prototyp zeigt Verläufe und Vergleiche, markiert aber nicht
automatisch Ausreißer oder plötzliche Abweichungen. Das ist eher ein
visuelles Analysewerkzeug als ein automatisches Überwachungssystem.

### Schwachpunkt 3: Zeitachse der Wellenformen

Die Einzelzyklus-Wellenformen werden nach Millisekunden innerhalb des
Zyklus ausgerichtet. Bei zyklusabhängigen Daueränderungen kann das die
Interpretation von Phasenverschiebungen beeinflussen.

---

## 6. Antworten auf mögliche Fragen

### Frage: Warum nicht einfach alle Rohdaten ins Dashboard laden?

Antwort: Die Rohdatenmenge ist zu groß für einen Browser. Selbst ein
lokaler Rechner würde beim Laden von Hunderten Millionen Zeilen und
Messpunkten sehr langsam oder gar unbrauchbar werden. Daher wird zuerst
offline auf per-Zyklus-Aggregation reduziert.

### Frage: Sind die Trends wirklich repräsentativ?

Antwort: Ja. Die Trend-Auswertung nutzt alle aktiven Zyklen. Es wird nicht
nur ein Sample geplottet, sondern die Daten werden in 3.000 chronologisch
sortierte Gruppen zusammengefasst, und pro Gruppe werden Mittelwert sowie
10./90. Perzentile berechnet.

### Frage: Was bedeutet „aktive Zyklen"?

Antwort: Aktive Zyklen sind solche, die nicht unmittelbar an einer Pause
angenommen werden. In der Datenvorverarbeitung wurden Pausenbereiche
gefiltert, um die Trendanalyse auf echten Betriebsbetrieb zu fokussieren.

### Frage: Kann ich einen Zyklus außerhalb der 1.500 Stichproben sehen?

Antwort: Nicht direkt. Das Dashboard erlaubt nur eine Auswahl aus dem
vorbereiteten Pool. Wenn ein eingegebener Zyklus nicht exakt im Pool
ist, wird der nächstgelegene Vertreter genutzt.

### Frage: Welche neuen Erkenntnisse liefert das Dashboard?

Antwort:
- Es macht langfristige Drift oder schleichende Veränderung sichtbar.
- Es zeigt, ob Peaks oder Mittelwerte über Monate breiter oder enger
  werden.
- Es erlaubt den Vergleich einzelner Zyklen mit einem Referenzzyklus,
  wodurch Abweichungen messbar werden.

---

## 7. Vorschlag zur Präsentation

1. Beginne mit der Problemstellung: große Datenmenge, langer Testlauf,
   Browser-Visualisierung ohne Server.
2. Erkläre den Offline-Workflow: Rohdaten → Zyklusstatistik → Trend/Pool
   → fertiges Dashboard.
3. Zeige die Visualisierung: Trend-Tab zuerst (Gesamtverlauf), dann
   Vergleichs-Tab (Detailzyklen).
4. Hebe die Transparenz hervor: Vollpopulation für Trends, ausgewählte
   Stichprobe für Detailansicht.
5. Nenne die Grenzen: Stichprobe ist repräsentativ, aber nicht vollständig;
   kein automatisches Alarm- oder Anomalie-Flagging.
6. Schließe mit dem Nutzen: schnelle, portable Analyse des Testverlaufs,
   solide Basis für weitere vertiefte Auswertung.

---

## 8. Stichworte für deine Erläuterung

- Offline-Vorverarbeitung
- DuckDB ASOF-Join
- Per-Zyklus-Aggregation
- Trend-Buckets + Perzentile
- Repräsentative Zyklusprobe
- Selbstständige HTML-Datei
- Statistische Ehrlichkeit
- Vergleichbarkeit trotz unterschiedlicher Einheiten
- Keine Live-Datenverbindung nötig

---

## 9. Praktische Formulierungen

- „Dieses Dashboard ist kein Live-Monitor, sondern eine
  Analyse-Snapshot-Datei, die auf einer robusten Offline-Pipeline beruht."
- „Die Trenddarstellung verwendet alle aktiven Zyklen, also ist sie nicht
  nur ein Zufallsstichprobe-Chart.“
- „Die Einzelzyklus-Ansicht ist bewusst repräsentativ und bezieht sich auf
  1.500 gleichmäßig verteilte Zyklen, um die Dateigröße handhabbar zu
  halten.“
- „Wir haben bewusst die Originaleinheiten beibehalten, um nicht durch
  umrechnete Werte die Interpretation zu verfälschen."
- „Wichtig ist: Es ist ein visuelles Analysewerkzeug, kein automatisches
  Alarm-System."

---

## 10. Nächste mögliche Erweiterungen

- Ereignismarkierungen für Wartungs-/Pausezeiten im Trenddiagramm.
- Automatische Ausreißer- oder Änderungssegment-Erkennung.
- Eine zusätzliche Ansicht für Dichte-/Heatmap-Darstellung, falls viele
  Zyklen gleichzeitig verglichen werden.
- Ein einzelnes Skript oder Makefile für die gesamte Regeneration.
- Versions-/Provenance-Metadaten direkt im Dashboard.
