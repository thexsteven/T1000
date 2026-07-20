# 3. Bestehende Vorverarbeitungs-Pipeline und identifizierte Lücken

## Herkunft

Die hier beschriebene Pipeline stammt aus einer vorangegangenen
Masterarbeit im selben Unternehmensumfeld (nicht Teil dieser Arbeit,
sondern deren Ausgangsbasis). Sie wandelt rohe Prüfstands-Aufzeichnungen
schrittweise in eine strukturierte, für Analysen nutzbare Form um. Die
Pipeline ist als Abfolge von zehn Verarbeitungsstufen konzipiert, von
denen zum Zeitpunkt dieser Arbeit acht tatsächlich implementiert sind;
die letzten beiden (Feature-Engineering und finale Datensatz-Erzeugung)
sind erst geplant.

## Die Pipeline-Stufen im Überblick

1. **Metadaten-Katalogisierung** — erfasst, welche Rohsignale mit
   welchen Eigenschaften überhaupt vorliegen.
2. **Signal-Auswahl** — wählt die für die Analyse relevanten
   Signalkanäle aus der Gesamtmenge verfügbarer Kanäle aus.
3. **Zeitstempel-Analyse** — berechnet Lücken-Statistiken je Signal, als
   Grundlage für spätere Schwellwert-Entscheidungen.
4. **Aufzeichnungssitzungs-Erkennung** — teilt die durchgehende
   Zeitreihe an großen zeitlichen Lücken in getrennte
   „Aufzeichnungssitzungen“, damit keine Zyklus-Erkennung über einen
   Prüfstands-Unterbruch (z. B. Wartung, Stillstand über Nacht) hinweg
   erfolgt.
5. **Zyklus-Erkennung** — leitet aus dem Positionssignal einzelne
   Bewegungszyklen ab, indem Über- und Unterschreitungen eines
   Bewegungsschwellwerts als Zyklusanfang bzw. -ende interpretiert
   werden; unvollständige Randzyklen werden verworfen.
6. **Zyklus-Auswahl** — wählt aus der Gesamtmenge erkannter Zyklen eine
   repräsentative Teilmenge aus, verteilt über Aufzeichnungssitzungen
   und Zeitabschnitte, begrenzt durch eine konfigurierbare Zielgröße.
7. **Multi-Sensor-Extraktion** — schneidet für die ausgewählten Zyklen
   alle Sensorsignale (nicht nur Position) im jeweiligen Zeitfenster
   heraus, in ihrer jeweils nativen Abtastrate (kein Resampling). Ein
   interner Zusatzschritt wählt daraus wenige Zyklen aus, die alle
   erforderlichen Signale mit ausreichender Abtastdichte enthalten und
   direkt aufeinanderfolgend („konsekutiv“) in derselben
   Aufzeichnungssitzung liegen — diese dienen als Validierungsbasis.
8. **Zyklus-Qualitätsprofilierung** — berechnet für jeden Zyklus und
   jedes Signal rein beschreibende Qualitätskennzahlen (fehlende
   Kanäle, Zeitstempel-Konsistenz, Abtastverhalten, Abdeckungsgrad
   innerhalb des Zyklus). Diese Stufe **entscheidet selbst nicht**,
   welche Zyklen brauchbar sind — sie liefert nur die Datenbasis, aus
   der später Schwellwerte abgeleitet werden können.
9. **Feature-Engineering** *(geplant, nicht implementiert)*.
10. **Finale Datensatz-Erzeugung** *(geplant, nicht implementiert)*.

Am Ende dieser acht implementierten Stufen existiert somit eine Menge
von Kandidaten-Zyklen mit begleitenden Qualitätskennzahlen — aber noch
**keine** abschließende Entscheidung, welche dieser Zyklen tatsächlich
in einen „Pool nutzbarer Daten“ aufgenommen werden sollen. Genau diese
fehlende Entscheidungslogik ist die Lücke, die der in dieser Arbeit
entwickelte Entscheidungsbaum (Kapitel 4) schließt.

## Identifizierte Lücken in der bestehenden Pipeline

Bei der Analyse der bestehenden Pipeline wurden mehrere methodische
Lücken festgestellt, die für die Bewertung der „Nutzbarkeit“ eines
Zyklus relevant sind, in der bisherigen Logik aber nicht abgedeckt
werden:

- **Keine Stillstandserkennung.** Es existiert keine dedizierte Logik,
  die erkennt, ob ein Signal innerhalb eines erkannten Zyklus tatsächlich
  in Bewegung ist oder z. B. durch einen eingefrorenen Sensor bzw. eine
  Kommunikationsunterbrechung fälschlich als „aktiver Zyklus“
  durchgeht. Die einzige vorhandene Bewegungs-/Ruhe-Unterscheidung dient
  ausschließlich der Bestimmung von Zyklusgrenzen selbst, nicht der
  Prüfung, ob die Bewegung *innerhalb* eines erkannten Zyklus plausibel
  ist.
- **Kein Mindestdauer-/Mindestbewegungsfilter.** Zyklusdauer und
  Positionsspanne werden zwar berechnet, aber nirgends als
  Ausschlusskriterium verwendet. Dadurch könnte theoretisch ein extrem
  kurzer oder extrem langer „Zyklus“ (z. B. ein einzelner Rauschausschlag
  über dem Bewegungsschwellwert, oder eine fälschlich über eine
  Prüfstandspause hinweg zusammengefasste Messreihe) unbemerkt als
  gültiger Zyklus akzeptiert werden.
- **Geschwindigkeit für Qualitätsbewertung ungenutzt.** Das
  Geschwindigkeitssignal wird zwar extrahiert und steht pro Zyklus zur
  Verfügung, wird aber an keiner Stelle der bestehenden Pipeline zur
  Beurteilung der Zyklus- oder Signalqualität herangezogen — obwohl es
  physikalisch der direktere Indikator für „Stillstand“ wäre als ein
  reiner Positions-Schwellwert.
- **Keine physikalische Plausibilitätsprüfung.** Es gibt keine
  systematische Prüfung, ob ein erkannter Zyklus physikalisch sinnvoll
  ist — etwa ob der volle Hub tatsächlich erreicht wurde, ob die Anzahl
  der Messwerte im erwarteten Bereich liegt, oder ob Signalwerte
  ungültig (nicht endliche Werte) bzw. über den gesamten Zyklus hinweg
  konstant („eingefroren“) sind.
- **Vorläufiger Positions-Schwellwert.** Der zentrale Schwellwert, ab
  dem das Positionssignal als „in Bewegung“ gilt, ist im Code an
  mehreren Stellen dupliziert und explizit als vorläufig markiert — er
  wurde ursprünglich ohne Rückgriff auf die tatsächliche Verteilung der
  Positionswerte im Ruhezustand festgelegt. Er funktioniert in der
  Praxis, sein Sicherheitsabstand zur beobachteten Ruhelage ist jedoch
  schmal und bisher nicht dokumentiert begründet.

Diese fünf Lücken bilden zusammen den fachlichen Ausgangspunkt für den
in Kapitel 4 beschriebenen Entscheidungsbaum: Jede Lücke entspricht
einer neuen Prüfebene bzw. einem neu zu begründenden Kriterium, das die
bestehende Pipeline ergänzt, ohne sie zu ersetzen.
