# 2. Versuchsaufbau und Daten

## Prüfstandsversuche (Dauerläufe / „Endurance Tests“)

Die zugrunde liegenden Daten stammen aus **Dauerlauf-Prüfstandsversuchen**
an elektrischen Linearaktuatoren („electric rodstyle actuators“). Bei
einem Dauerlauf wird ein Prüfling über einen sehr langen Zeitraum
(mehrere Monate, im Extremfall über ein halbes Jahr) kontinuierlich in
einer sich wiederholenden Bewegung betrieben, um Verschleiß- und
Alterungsverhalten unter realistischer Dauerbelastung zu beobachten.
Solche Versuche sind die Standardmethode, um die Lebensdauer und
Zuverlässigkeit von Aktuatoren nachzuweisen, bevor sie in
sicherheitsrelevanten industriellen Anwendungen eingesetzt werden.

Die Rohdaten liegen als große, hive-partitionierte Parquet-Dateien vor
(ein spaltenorientiertes Binärformat für sehr große Datenmengen), in
denen jede Zeile eine einzelne Sensormessung zu einem Zeitstempel
darstellt. Über die gesamte Versuchsdauer eines einzelnen Prüflings
kommen dabei Größenordnungen von mehreren hundert Millionen
Einzelmessungen zusammen, die zu Millionen von Einzelzyklen gehören.

## Versuchsserien

In diesem Projekt werden Daten aus mehreren solcher Dauerlaufversuche
betrachtet, die in unternehmensinterner Nomenklatur als Versuchsserien
mit fortlaufender Nummer bezeichnet werden (in den Analysedokumenten
z. B. als zwei getrennte Serien geführt). Jede Serie umfasst einen oder
mehrere konkrete Prüflinge/Prüfläufe. Die Serien unterscheiden sich u. a.
in Aufzeichnungszeitraum, Anzahl vorhandener Sensorsignale und Umfang
der Rohdaten, folgen aber demselben grundsätzlichen Aufbau: ein
Aktuator, der fortlaufend eine vorgegebene Bewegungstrajektorie abfährt,
während mehrere Sensoren parallel mit unterschiedlichen Abtastraten
aufzeichnen.

Aus methodischer Sicht ist wichtig, dass sich Erkenntnisse (Kriterien,
Schwellwerte, Filterlogik), die an einer Versuchsserie hergeleitet
werden, nicht automatisch unverändert auf eine andere Serie übertragen
lassen — Aufzeichnungsbedingungen, Sensorumfang und ggf. auch die
physikalische Auslegung des Prüflings können variieren. Das ist einer
der Gründe, warum Schwellwerte in dieser Arbeit **datengetrieben** aus
den beobachteten Verteilungen abgeleitet werden, statt sie fest zu
verdrahten.

## Zyklusdefinition

Der Aktuator ist **positionsgeregelt**: Er folgt einer vorgegebenen
Bewegungstrajektorie, die im Kern aus einer Hin- und Rückbewegung
(„out and back“) zwischen einer Ruheposition und einer definierten
Zielposition (dem vollen Hub) besteht. Ein solcher **Bewegungszyklus**
ist die zentrale analytische Grundeinheit dieser Arbeit: Alle
Qualitätsprüfungen und Visualisierungen beziehen sich auf einzelne
Zyklen, nicht auf beliebige Zeitfenster.

Ein Zyklus wird technisch dadurch abgegrenzt, dass das Positionssignal
aus der Ruhelage heraus einen Bewegungsschwellwert überschreitet
(Zyklusbeginn) und später wieder darunter zurückkehrt (Zyklusende). Die
sich daraus ergebende typische Zyklusdauer liegt im Bereich weniger
Sekunden. Eine in einer früheren, vorläufigen Projektnotiz kursierende
kürzere Zyklusdauer (rund 1,8 Sekunden) hat sich im Projektverlauf als
veraltet/unzutreffend herausgestellt und wurde durch eine anhand der
tatsächlichen Zyklusdaten empirisch bestätigte, deutlich robustere
Schätzung ersetzt (siehe Kapitel 3 und 4 zur Herleitung und
Validierung von Zyklusgrenzen). Für die methodische Darstellung in
dieser Arbeit ist relevant, **dass** die Zyklusdauer aus den Daten
empirisch bestimmt und nicht als fixer Literaturwert übernommen wird —
dieser iterative Korrekturprozess ist selbst ein Beispiel dafür, warum
eine begründete, datengetriebene Kriterien-Herleitung notwendig ist.

## Sensorsignale

Für jeden Bewegungszyklus werden mehrere kontinuierliche Sensorsignale
parallel aufgezeichnet, die jeweils eine andere physikalische Größe
erfassen und unterschiedliche Abtastraten haben:

- **Position** — die Referenzgröße zur Erkennung von Zyklusgrenzen, da
  der Aktuator positionsgeregelt ist.
- **Geschwindigkeit** — abgeleitete Bewegungsgröße, bislang in der
  bestehenden Pipeline zwar extrahiert, aber für Qualitätsprüfungen
  ungenutzt (siehe Kapitel 3, Lücke „Geschwindigkeit ungenutzt“).
- **Strom** — elektrische Antriebsgröße, u. a. Grundlage für einen aus
  Strom und Position abgeleiteten Kennwert als Näherung für eine
  Hysterese-/Kraftschleife (da kein direktes Kraft-/Drehmomentsignal
  vorliegt).
- **Druck** — hydraulische bzw. pneumatische Zusatzgröße je nach
  Aktuatortyp.
- **Temperatur** — mehrere Messstellen (z. B. Motor, Spindelmutter,
  Festlager), mit deutlich geringerer Abtastrate als die schnellen
  Bewegungssignale.
- **Vibration (x/y/z)** — dreiachsige Schwingungsmessung mit sehr hoher
  Abtastrate, dadurch pro Zyklus mit Abstand die meisten Einzelwerte
  aller Signale.

Die Signale unterscheiden sich stark in ihrer nativen Abtastrate: Die
Positions-/Geschwindigkeits-/Strom-Signale liegen im Bereich von
einigen Dutzend Messwerten pro Zyklus, Druck und Temperatur deutlich
darunter, Vibration dagegen um Größenordnungen darüber. Diese
Heterogenität ist einer der Gründe, warum die bestehende Pipeline
bewusst **kein Resampling/Interpolieren** auf eine gemeinsame Rate
vornimmt, sondern jedes Signal in seiner nativen Auflösung belässt (vgl.
Kapitel 3).

## Datenmengen-Charakteristik

Grundsätzlich gilt für alle betrachteten Versuchsserien: Die Rohdaten
sind um Größenordnungen zu groß, um sie vollständig in üblichen
Analyse- oder Visualisierungswerkzeugen im Arbeitsspeicher zu halten
oder unverdichtet in einen Bericht einzubetten. Ein einzelner
Dauerlaufversuch erzeugt typischerweise mehrere hunderttausend bis
mehrere Millionen Bewegungszyklen und, über alle Sensorsignale
zusammengenommen, mehrere hundert Millionen Einzelmesswerte. Diese
Größenordnung prägt sowohl die Wahl der Werkzeuge (spaltenorientierte,
lazy-ladende Abfragen statt vollständigem Einlesen) als auch die
grundsätzliche Notwendigkeit einer mehrstufigen Verdichtung, bevor Daten
in einem interaktiven Bericht dargestellt werden können (siehe Kapitel
5).
