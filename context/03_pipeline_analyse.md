# 3. Bestehende Vorverarbeitungs-Pipeline und identifizierte Lücken

## Herkunft

Die hier beschriebene Pipeline stammt aus einer vorangegangenen
Masterarbeit (Fatemeh Heydari) im selben Unternehmensumfeld — sie ist
nicht Teil dieser Arbeit, sondern deren Ausgangsbasis. Sie wandelt rohe
Prüfstands-Aufzeichnungen schrittweise in strukturierte, für Analysen
nutzbare Bewegungszyklen um und — seit Pipeline-Version **V2.1**
(Stand 2026-07-22) — validiert und verwirft diese zusätzlich anhand
automatisch aus den Daten abgeleiteter, statistischer Schwellwerte.

In ihrer maßgeblichen Fassung (V2.1) ist die Pipeline als Abfolge von
**dreizehn Verarbeitungsstufen** konzipiert, von denen zum Zeitpunkt
dieser Arbeit zehn implementiert sind; die letzten drei
(Feature-Engineering, finale Datensatz-Erzeugung sowie Machine Learning /
Anomalieerkennung) sind erst geplant. Die im Folgenden verwendete
Stufennummerierung folgt der autoritativen Stufengliederung der
Masterarbeit (`thesis_pipeline`, V2.1).

## Die Pipeline-Stufen im Überblick

1. **Metadaten-Integration** — erfasst über die Metadaten, welche
   Experimente, Sensoren und Signale (UUIDs, Einheiten,
   Knoten-Hierarchie) überhaupt vorliegen.
2. **Automatische Signal-Erkennung** — identifiziert den benötigten
   Sensor automatisch über Experimentname und semantischen Signaltyp,
   statt Signal-UUIDs manuell anzugeben.
3. **Effizientes Messwert-Laden** — lädt aus dem milliardenschweren
   Rohdatenbestand nur das benötigte Signal im benötigten Zeitintervall
   (Predicate Pushdown, Partition Pruning), da ein vollständiges Laden
   nicht praktikabel ist.
4. **Zeitstempel-Analyse** — berechnet Lücken-Statistiken je Signal, als
   Grundlage für spätere Schwellwert-Entscheidungen.
5. **Aufzeichnungssitzungs-Erkennung** — teilt die durchgehende
   Zeitreihe an großen zeitlichen Lücken in getrennte
   „Aufzeichnungssitzungen“, damit keine Zyklus-Erkennung über einen
   Prüfstands-Unterbruch (z. B. Wartung, Stillstand über Nacht) hinweg
   erfolgt.
6. **Positionsbasierte Zyklus-Erkennung** — leitet aus dem
   Positionssignal einzelne Bewegungszyklen ab, indem Über- und
   Unterschreitungen eines Bewegungsschwellwerts als Zyklusanfang bzw.
   -ende interpretiert werden; unvollständige Randzyklen werden
   verworfen.
7. **Multi-Sensor-Zyklus-Extraktion** — schneidet für die erkannten
   Zyklen alle Sensorsignale (nicht nur Position) im jeweiligen
   Zeitfenster in ihrer nativen Abtastrate heraus (kein Resampling).
   Eine fehlende optionale Signalspur (typisch: die getaktete Vibration)
   führt bewusst **nicht** zum Verwerfen des Zyklus.
8. **Zyklus-Qualitätsprofilierung** — berechnet für jeden Zyklus und
   jedes Signal rein **beschreibende** Qualitätskennzahlen (fehlende
   Kanäle, `constant_signal`, Abdeckungsgrad, Anzahl (nicht-)endlicher
   Werte, Zeitstempel-Konsistenz, Abtastverhalten). Diese Stufe
   **entscheidet selbst nicht** über die Brauchbarkeit — sie liefert die
   Verteilungen, aus denen die nächste Stufe Schwellwerte ableitet.
9. **Validierungsregel-Generierung** *(neu in V2.1)* — leitet die
   Validierungsschwellwerte automatisch und datengetrieben aus der
   Profiling-Verteilung ab (robuster Median/MAD, Quantil-Fallback) und
   trennt dabei **harte Regeln** (logische/fachliche Zwänge) von
   **gelernten Regeln** (statistische Grenzen). Bei zu kleiner
   Referenzpopulation werden Regeln explizit als `provisional` markiert.
10. **Datensatz-Validierung** *(neu in V2.1)* — wendet die eingefrorenen
    Regeln aus Stufe 9 auf jeden profilierten Zyklus an und ist die
    **einzige Stufe, die Zyklen ablehnt**. Sie klassifiziert jeden
    Zyklus als `valid_core_cycle`, `valid_complete_multisensor_cycle`
    oder `invalid_cycle` und protokolliert Ablehnungsgründe (z. B.
    `duration_below_lower_bound`, `position_stroke_out_of_range`), ohne
    Rohdaten zu löschen.
11. **Feature-Engineering** *(geplant, nicht implementiert)*.
12. **Finale Datensatz-Erzeugung** *(geplant, nicht implementiert)*.
13. **Machine Learning / Anomalieerkennung** *(geplant, nicht
    implementiert)*.

## Was sich mit Pipeline-Version V2.1 verändert hat

Eine frühere Fassung dieser Analyse ging davon aus, dass die Pipeline die
Zyklen zwar profiliert, aber **keine** abschließende Entscheidung über
ihre Aufnahme in einen „Pool nutzbarer Daten“ trifft — dass also genau
diese fehlende Entscheidungslogik die zentrale Lücke sei. Mit V2.1
treffen **die Stufen 9–10 diese Entscheidung nun selbst**: datengetrieben,
statistisch und mit protokollierten Ablehnungsgründen. Die ursprünglich
angenommene Lücke „keine Zyklus-Zulassung“ ist damit **geschlossen**.

Entscheidend für die Abgrenzung dieser Arbeit ist jedoch die *Art* dieser
Validierung: Die Stufen 9–10 beantworten eine **relative** Frage — „ist
dieser Zyklus im Vergleich zur Population ungewöhnlich?“ — anhand von
Schwellwerten, die aus einer Population gelernt werden, die gesunde und
degradierte Zyklen mischt. Diese gelernte „Normalität“ kann mit
wachsendem Fehleranteil mitwandern. Was die Pipeline weiterhin nicht
leistet, ist eine **absolute, populationsunabhängige physikalische**
Beurteilung, ob ein Zyklus überhaupt brauchbar ist. Genau hier setzt der
Entscheidungsbaum aus Kapitel 4 an — nicht mehr als die fehlende
Zulassungsentscheidung, sondern als **physikalischer Querschnitt und
Transparenzschicht auf der statistischen Validierung**.

## Verbleibende Lücken in der bestehenden Pipeline

Auch mit V2.1 bleiben mehrere methodische Lücken für die Beurteilung der
„Nutzbarkeit“ eines Zyklus offen. Sie bilden den fachlichen
Ausgangspunkt für den in Kapitel 4 beschriebenen Entscheidungsbaum:

- **Keine In-Zyklus-Stillstandserkennung.** Die Profilierung erkennt mit
  `constant_signal` nur ein Signal, das über den *gesamten* Zyklus
  konstant ist. Ein kurzer eingefrorener Abschnitt *innerhalb* eines
  ansonsten bewegten Zyklus (z. B. Sensor-Freeze oder
  Kommunikationsunterbruch) bleibt unentdeckt und geht als aktiver Zyklus
  durch. Eine gleitende Fensterprüfung *innerhalb* des Zyklus fehlt
  vollständig — dies ist die klarste genuin neue Prüfung dieser Arbeit.
- **Keine Mindest-Sitzungsgröße.** Zyklen aus sehr kurzen, nicht
  repräsentativen Aufzeichnungssitzungen (z. B. Inbetriebnahme- oder
  abgebrochene Läufe) werden nicht ausgeschlossen. Eine solche Prüfung
  existiert in der Pipeline nicht.
- **Kein absoluter physikalischer Boden.** Die Stufen 9–10 prüfen Dauer,
  Hub und Messwertzahl gegen *gelernte, populationsrelative* Grenzen. Ein
  Zyklus, der physikalisch unmöglich ist, aber nahe dem Populationsmedian
  liegt, kann so unbemerkt passieren — insbesondere, wenn eine ganze
  Charge gemeinsam degradiert und den statistischen Referenzbereich
  mitverschiebt. Eine gegen *absolute* physikalische Werte (voller Hub,
  plausible Dauer, erwartete Messwertzahl, endliche Werte) geprüfte
  Untergrenze ergänzt die statistische Regel als eigene, andersartige
  Fehlerklasse (vgl. ADR-T02).
- **Geschwindigkeit für die Stillstandsprüfung ungenutzt.** Das
  Geschwindigkeitssignal wird zwar in Stufe 8 mit-profiliert, aber an
  keiner Stelle als physikalischer Indikator für Stillstand herangezogen
  — obwohl es der direktere Indikator wäre als ein reiner
  Positions-Schwellwert. Die geschwindigkeitsbasierte Stillstandsprüfung
  setzt zudem eine bislang nicht abschließend verifizierte Kalibrierung
  des Geschwindigkeitssignals voraus (vgl. ADR-T05).
- **Vorläufige Segmentierungs-Schwellwerte.** Die beiden zentralen
  Schwellwerte, die Sitzungen und Zyklen überhaupt erst schneiden — die
  Sitzungslücke (`3600 s`) und die Bewegungsschwelle der Zyklus-Erkennung
  (`Position > 1.0`) — liegen *oberhalb* der Regelgenerierung (Stufe 9)
  und sind weiterhin als vorläufig markiert, teils im Code dupliziert und
  nicht aus der Datenverteilung hergeleitet. Ihr Sicherheitsabstand zur
  beobachteten Ruhelage ist schmal und nicht dokumentiert begründet.
  Diese Arbeit leitet beide Werte datenbasiert neu her und gibt sie zur
  Anwendung an die Pipeline zurück (vgl. ADR-T06), ohne die Segmentierung
  selbst zu reimplementieren.

Jede dieser Lücken entspricht einer Prüfebene bzw. einem neu zu
begründenden Kriterium des in Kapitel 4 beschriebenen Entscheidungsbaums,
das die bestehende Pipeline **ergänzt**, ohne sie zu ersetzen — und, um
das Reifegradsystem erweitert, zugleich die Belastbarkeit *jedes*
Kriteriums, auch der pipeline-eigenen statistischen Regeln, transparent
macht.
