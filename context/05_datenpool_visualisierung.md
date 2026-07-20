# 5. Datenpool-Ableitung und HTML-Zyklus-Overlay

## Vom Entscheidungsbaum zum Datenpool

Der in Kapitel 4 beschriebene Entscheidungsbaum ist zunächst eine
fachliche Prüflogik. Ihre praktische Umsetzung besteht darin, diese
Logik auf **alle** aufgezeichneten Kandidaten-Zyklen einer
Versuchsserie anzuwenden und daraus zwei Ergebnisse abzuleiten:

1. Den eigentlichen **Datenpool** — die Teilmenge aller Zyklen, die
   sämtliche vier Prüfebenen bestanden hat und damit als „nutzbar“ für
   weiterführende Analysen und potenzielle Modellbildung gilt.
2. Ein **Ablehnungsprotokoll** — für jeden nicht aufgenommenen Zyklus
   wird festgehalten, an welcher Ebene und aus welchem konkreten Grund
   er ausgeschlossen wurde (z. B. „Dauer-Ausreißer“, „unvollständiger
   Hub“, „Stillstand/eingefrorenes Signal“, „fehlende Signale“). Dieses
   Protokoll ist selbst ein wichtiges Analyseergebnis: Es zeigt
   quantitativ, wie viele Zyklen an welcher Stelle „hängenbleiben“, und
   liefert damit den empirischen Beleg dafür, dass der Entscheidungsbaum
   tatsächlich reale, andernfalls unbemerkte Problemfälle herausfiltert.

Der Datenpool ist damit keine willkürliche Stichprobe, sondern eine
**geprüfte, begründete Teilmenge** der Gesamtaufzeichnung — jeder
enthaltene Zyklus hat alle Qualitätskriterien nachweislich erfüllt, und
jeder ausgeschlossene Zyklus trägt einen dokumentierten, nachvollziehbaren
Grund.

## Warum eine Visualisierung auf dem Pool statt auf Rohdaten aufsetzt

Die zweite Säule des eigenen Beitrags ist eine browserbasierte
Visualisierung, die einzelne Bewegungszyklen als überlagerte
Signalverläufe darstellt (das „Cycle-Overlay“). Diese Visualisierung
baut bewusst auf dem geprüften Datenpool auf und **nicht** direkt auf
den unverarbeiteten Rohdaten. Dafür gibt es mehrere zusammenhängende
Gründe:

- **Datenmenge.** Die Rohaufzeichnung eines einzelnen Dauerlaufs umfasst
  Größenordnungen von Millionen Zyklen und hunderten Millionen
  Einzelmesswerten (siehe Kapitel 2) — das ist um Größenordnungen zu
  viel, um es direkt, unverdichtet in einem interaktiven Browser-Bericht
  darzustellen, ohne dass die Anwendung unbrauchbar langsam wird oder
  abstürzt.
- **Inhaltliche Aussagekraft.** Eine Überlagerung roher, ungeprüfter
  Zyklen würde Artefakte (Stillstandsphasen, unvollständige Hübe,
  Sensorausfälle) optisch gleichberechtigt neben echten, gültigen
  Zyklen darstellen. Ein Testingenieur, der die Überlagerung betrachtet,
  könnte einen aus einem defekten Sensor stammenden „Ausreißerzyklus“
  fälschlich für eine reale Verschleißerscheinung des Aktuators halten.
  Indem nur geprüfte Pool-Zyklen dargestellt werden, zeigt die
  Visualisierung tatsächliche Trends im Betriebsverhalten, nicht
  Datenqualitätsrauschen.
- **Konsistenz mit dem übrigen Projektziel.** Da der Datenpool ohnehin
  die vorgesehene Grundlage für spätere Modellbildung sein soll, stellt
  die Visualisierung genau das dar, worauf sich auch andere
  nachgelagerte Analysen stützen würden — sie ist damit ein direktes,
  visuelles Werkzeug, um die Qualität und Charakteristik desselben
  Datensatzes zu prüfen, der auch anderswo verwendet wird.

## Grundprinzip der Visualisierungs-Pipeline

Da auch die geprüfte Poolmenge noch zu groß ist, um sie vollständig in
voller Auflösung in eine einzelne Browserdatei einzubetten, folgt die
Visualisierung dem Prinzip: **einmalig offline verdichten, nur das
kompakte Ergebnis ausliefern, alle Interaktivität im Browser auf dieser
kleinen Ergebnismenge ausführen.** Konkret werden aus dem
(vollständigen) Pool zwei komplementäre, unterschiedlich stark
verdichtete Sichten erzeugt:

- Eine **Trend-Sicht**, die *alle* aktiven Zyklen des Pools
  berücksichtigt, indem sie den gesamten Betriebszeitraum in eine feste
  Anzahl chronologischer Zeitabschnitte („Buckets“) unterteilt und pro
  Abschnitt und Kenngröße Mittelwert sowie ein unteres/oberes Perzentil
  berechnet. Diese Sicht ist statistisch exakt über die volle
  Poolmenge, zeigt also einen ehrlichen Trend über die gesamte
  Lebensdauer, nicht nur über eine Stichprobe.
- Eine **Vergleichs-Sicht**, die eine begrenzte, gleichmäßig über den
  gesamten aktiven Zeitraum verteilte Stichprobe von Einzelzyklen
  vollständig mit ihrem Signalverlauf einbettet, damit einzelne Zyklen
  im Detail übereinandergelegt und miteinander verglichen werden können.
  Diese Sicht wird in der Benutzeroberfläche explizit als
  „repräsentative Teilmenge“ gekennzeichnet, um zu vermeiden, dass sie
  fälschlich als vollständige Abbildung aller Zyklen missverstanden
  wird.

Beide Sichten werden vorab offline berechnet und als kompakte,
strukturierte Datenpakete in eine einzelne, eigenständig lauffähige
HTML-Datei eingebettet. Diese Datei benötigt weder einen Server noch
eine Datenbankverbindung zur Laufzeit — sie lässt sich per Doppelklick
öffnen, was sie für den täglichen Gebrauch durch Testingenieure ohne
zusätzliche IT-Infrastruktur praktikabel macht (vgl. Zielsystem in
Kapitel 1).

## Bezug zur Praxissemesterarbeit vs. Aufgabenstellung

Wichtig für die Priorisierung dieser Arbeit ist, dass die eigentliche
Kriterien-/Entscheidungsbaum-Arbeit (Kapitel 3–4) als der methodisch
zentrale, für das Verfassen der schriftlichen Arbeit vorrangige Teil
gilt, während die HTML-Visualisierung des Pools inhaltlich als
nachgelagerter Schritt eingeordnet ist, der zeitlich parallel zum
Schreiben der Arbeit weiterentwickelt werden kann, ohne den
Schreibbeginn zu blockieren.
