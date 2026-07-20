# 6. Stand der Umsetzung und offene Punkte

Dieses Kapitel hält den Bearbeitungsstand zum Zeitpunkt der
Erstellung dieser Kontextdateien fest. Es dient als Momentaufnahme —
nicht als endgültiges Ergebnis — und sollte beim Schreiben mit dem
tatsächlichen, zu diesem Zeitpunkt aktuellen Projektstand abgeglichen
werden.

## Bereits umgesetzt

- **Analyse der bestehenden Vorverarbeitungs-Pipeline** (Kapitel 3):
  Alle acht implementierten Pipeline-Stufen sowie deren jeweils
  verwendete Kriterien wurden systematisch erfasst und den in Kapitel 4
  beschriebenen Reifegraden zugeordnet. Dabei wurden die konkreten
  Lücken (fehlende Stillstandserkennung, fehlender
  Mindestdauer-/Mindestbewegungsfilter, ungenutztes
  Geschwindigkeitssignal, fehlende physikalische
  Plausibilitätsprüfung, unbegründeter Bewegungsschwellwert) identifiziert
  und dokumentiert.
- **Entwurf des vierstufigen Entscheidungsbaums** (Kapitel 4): Eine
  erste, ausführlich dokumentierte Entwurfsversion liegt vor, inklusive
  Verweisen auf die jeweiligen Code-Quellen der bestehenden Pipeline für
  jedes bereits implementierte Kriterium. Für jedes Kriterium ist der
  Reifegrad vermerkt, und offene Diskussionspunkte sind explizit als
  solche markiert, um sie in Abstimmungsgesprächen mit den fachlich
  Verantwortlichen gezielt klären zu können.
- **Ausführung der Zyklus-Qualitätsprofilierung (Pipeline-Stufe 8) im
  vollen Umfang**: Diese zuvor nur mit reduzierten Testmengen gelaufene
  Stufe wurde auf die vollständige Datenmenge einer Versuchsserie
  ausgeweitet, um reale Verteilungen als Grundlage für die noch offenen
  Ebene-4-Schwellwerte zu erhalten (statt diese weiterhin nur als
  Platzhalter zu führen).
- **Erste Version des HTML-Cycle-Overlays und eines interaktiven
  Lifetime-Dashboards**: Eine dreistufige, offline laufende
  Verdichtungspipeline (Rohdaten → Zyklus-Kennzahlen → kompakte
  Trend-/Stichproben-Datensätze → eingebettete, eigenständig lauffähige
  HTML-Datei) wurde für eine Versuchsserie umgesetzt und funktionsfähig
  demonstriert, inklusive Trend-Übersicht über die gesamte Laufzeit und
  einer Detail-Vergleichsansicht auf Basis einer repräsentativen
  Zyklus-Stichprobe.

## Offene Punkte

- **Abstimmung mit den fachlich Verantwortlichen zu mehreren
  Kernkriterien**: Insbesondere die Herleitung des zentralen
  Bewegungsschwellwerts für die Zyklus-Erkennung, der Umgang mit einer
  dokumentierten Inkonsistenz beim Schwellwert für die
  Aufzeichnungssitzungs-Trennung (an einer Stelle als endgültig
  freigegeben, an anderer Stelle weiterhin als vorläufig markiert), die
  physikalische Kalibrierung/Skalierung des Geschwindigkeitssignals
  (Voraussetzung für die geschwindigkeitsbasierte
  Stillstandsdefinition), sowie eine Mindestgröße für gültige
  Aufzeichnungssitzungen sind zum jetzigen Stand noch nicht final
  geklärt.
- **Endgültige Festlegung der Ebene-4-Schwellwerte**: Die
  Signalqualitäts-Kriterien der obersten Prüfebene (Abdeckungsgrad,
  maximale Zeitlücke innerhalb eines Zyklus, Erkennung eingefrorener
  Signale) sind methodisch beschrieben, aber ihre konkreten
  Zahlenwerte müssen noch aus den neu erzeugten
  Qualitätsprofilierungs-Verteilungen abgeleitet und im
  Entscheidungsbaum von „noch offen“ auf „begründet festgelegt“
  überführt werden.
- **Implementierung des Pool-Filter-Moduls**: Der Entscheidungsbaum ist
  bislang als dokumentierte Prüflogik beschrieben; die tatsächliche
  Software-Komponente, die diese Logik automatisiert auf die
  vollständige Zyklusmenge anwendet und Pool sowie
  Ablehnungsprotokoll erzeugt, ist noch zu implementieren.
- **Vollständige Ausführung über die gesamte Zyklusmenge und Auswertung
  der Ablehnungsstatistik**: Sobald das Pool-Filter-Modul steht, muss es
  über die gesamte verfügbare Zyklusmenge einer Versuchsserie laufen,
  damit die daraus resultierende Ablehnungsstatistik (wie viele Zyklen
  wurden an welcher Ebene aus welchem Grund abgelehnt) als zentrales,
  empirisches Ergebniskapitel der Arbeit vorliegt.
- **Ausweitung der Visualisierung auf weitere Versuchsserien und
  Signale**: Das Cycle-Overlay/Dashboard wurde bislang exemplarisch für
  eine Versuchsserie umgesetzt; eine Ausweitung auf weitere
  Versuchsserien sowie eine Einbindung bislang nicht dargestellter
  Signale (insbesondere der hochfrequenten Vibrationssignale) ist als
  Erweiterung vorgesehen, blockiert aber nicht den Kern der
  Kriterien-/Entscheidungsbaum-Arbeit.
- **Formale Freigabe der Kriteriensammlung**: Eine zusammenfassende
  Übersichtsdarstellung (Pipeline-Überblick, Entscheidungsbaum,
  Stillstandsdefinition) soll den Vorgesetzten zur Freigabe vorgelegt
  werden, bevor die entsprechenden Kriterien in der schriftlichen
  Arbeit als „begründet und final“ dargestellt werden.

## Einordnung für die schriftliche Arbeit

Aus diesem Stand ergibt sich eine naheliegende Kapitelstruktur: Das
Methodik-Kapitel der Arbeit kann sich unmittelbar am Entscheidungsbaum
(Kapitel 4) orientieren, während das Ergebnis-Kapitel auf der
Ablehnungsstatistik aus der vollständigen Anwendung des Pool-Filters
aufbauen sollte, sobald diese vorliegt. Bis dahin sollten in der Arbeit
Formulierungen gewählt werden, die den vorläufigen Charakter einzelner
Schwellwerte (Reifegrade „provisorisch“, „nicht begründet“ bzw.
„inkonsistent“, siehe Kapitel 4) korrekt wiedergeben, statt sie als
bereits abschließend validiert darzustellen.
