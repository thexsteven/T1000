# 1. Projektrahmen

## Kontext

Diese Arbeit (Arbeitstitel „T1000“) entsteht im Rahmen eines
Praxissemesters (DHBW) bei einem Industrieunternehmen, das elektrische
Linearaktuatoren („electric rodstyle actuators“) entwickelt und deren
Zuverlässigkeit über Dauerlauf-Prüfstandsversuche nachweist. Während
dieser Dauerläufe zeichnen Prüfstände hochfrequente Sensordaten auf
(Position, Geschwindigkeit, Strom, Druck, Temperatur, Vibration). Diese
Rohdaten sollen langfristig als Trainingsgrundlage für datengetriebene
Modelle (z. B. Zustandsüberwachung, Restlebensdauer-Schätzung) dienen.

## Forschungsfrage

Die zentrale Forschungsfrage der Arbeit lautet:

> **„Wie kommt man von einer sehr großen Menge automatisch aufgezeichneter
> Prüfstandsdaten zu einem qualitativ hochwertigen, vertrauenswürdigen
> Datensatz, der als Grundlage für weiterführende Analysen und
> Modellbildung geeignet ist?“**

Rohdaten aus industriellen Prüfständen sind nicht automatisch
„brauchbar“: Aufzeichnungen enthalten Lücken, Sensorausfälle,
Prüfstandspausen, unvollständige Bewegungszyklen und andere Artefakte,
die eine spätere Auswertung verfälschen würden, wenn sie unbemerkt
bleiben. Die Arbeit untersucht systematisch, **nach welchen Kriterien**
ein aufgezeichneter Bewegungszyklus als „nutzbar“ gelten darf, **wie
diese Kriterien begründet** werden können (statt als unbegründete
„Magic Numbers“ im Code zu existieren), und **wie eine solche
Filterlogik nachvollziehbar und prüfbar** umgesetzt wird.

## Abgrenzung: Eigener Beitrag vs. Vorarbeit

Es existiert bereits eine umfangreiche Vorverarbeitungs-Pipeline aus
einer vorangegangenen Masterarbeit einer anderen Person im selben
Unternehmensumfeld. Diese Pipeline wandelt rohe, hive-partitionierte
Prüfstands-Aufzeichnungen in strukturierte Bewegungszyklen um und
extrahiert daraus Merkmale für mehrere Sensorsignale. Sie ist die
**Datenbasis**, auf der dieser Praxissemester-Beitrag aufbaut — sie
wird nicht neu geschrieben, sondern analysiert, geprüft und ergänzt.

Der eigene Beitrag dieser Arbeit (T1000) umfasst konkret drei Bausteine:

1. **Entscheidungsbaum für die Datenqualitätsprüfung** — eine
   systematische, mehrstufige Prüflogik, die für jeden aufgezeichneten
   Bewegungszyklus entscheidet, ob er in den „Pool nutzbarer Daten“
   aufgenommen oder mit einem dokumentierten Grund abgelehnt wird. Dabei
   werden bestehende, aber unbegründete Schwellwerte der Vorarbeit
   aufgegriffen, hinterfragt und nach Möglichkeit empirisch neu
   hergeleitet, und es werden fehlende Prüfschritte (z. B. Erkennung von
   Stillstands- oder Ausreißerzyklen) neu ergänzt.
2. **Datenpool-Ableitung** — die praktische Umsetzung dieses
   Entscheidungsbaums als Filterschritt, der aus der Gesamtmenge
   aufgezeichneter Zyklen den geprüften Teildatensatz erzeugt, inklusive
   eines nachvollziehbaren Ablehnungsprotokolls (welcher Zyklus wurde
   warum ausgeschlossen).
3. **HTML-Zyklus-Overlay / Dashboard-Visualisierung** — eine
   browserbasierte, ohne Serverinfrastruktur lauffähige Visualisierung,
   die Bewegungszyklen aus dem geprüften Datenpool überlagert darstellt
   und so Trends und Auffälligkeiten über die Lebensdauer eines
   Prüflings sichtbar macht.

Nicht Teil dieser Arbeit ist die eigentliche Vorverarbeitungs-Pipeline
selbst (Zyklus-Erkennung, Signal-Extraktion) sowie jegliche
Modellbildung (maschinelles Lernen) auf Basis des fertigen Datenpools —
beides ist Gegenstand der referenzierten Masterarbeit bzw. potenzieller
Anschlussarbeiten.

## Zielsystem

Das langfristige Zielbild, auf das die Arbeit hinarbeitet, ist ein
**täglich aktualisiertes Dashboard für Testingenieure** am Prüfstand:
eine kompakte, verständliche Übersicht, die zeigt, wie viele Zyklen an
einem Prüftag aufgezeichnet wurden, wie viele davon die
Qualitätsprüfung bestanden haben, welche Zyklen aus welchem Grund
verworfen wurden, und wie sich zentrale Kenngrößen (z. B. Zyklusdauer,
Bewegungsverhalten) über die Zeit entwickeln. Ein solches Dashboard soll
es Testingenieuren ohne Data-Science-Hintergrund ermöglichen, auf einen
Blick zu erkennen, ob die laufende Datenaufzeichnung „gesund“ ist, statt
das erst am Ende eines mehrmonatigen Dauerlaufs im Nachhinein
festzustellen. Der Entscheidungsbaum liefert dafür die fachliche Logik,
der Datenpool die geprüfte Datengrundlage, und das Cycle-Overlay das
visuelle Element.
