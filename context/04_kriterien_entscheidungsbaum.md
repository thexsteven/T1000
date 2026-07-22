# 4. Entscheidungsbaum und Kriterien-Reifegradsystem

## Grundidee

Um die in Kapitel 3 beschriebenen Lücken zu schließen und gleichzeitig
die bestehenden, teils unbegründeten Kriterien der Vorarbeit
transparent zu machen, wird ein **mehrstufiger Entscheidungsbaum**
entwickelt. Er beantwortet für jeden aufgezeichneten Bewegungszyklus die
Frage: „Gehört dieser Zyklus in den Pool nutzbarer Daten — und wenn
nicht, warum nicht?“ Ein Zyklus muss dabei alle Ebenen des Baums von
oben nach unten bestehen; scheitert er an einer Ebene, wird er mit
einem dokumentierten Ablehnungsgrund aus dem Pool ausgeschlossen, aber
nicht stillschweigend verworfen — jede Ablehnung bleibt nachvollziehbar
protokolliert.

Der Baum ist bewusst so aufgebaut, dass er die bestehende Pipeline aus
Kapitel 3 **nicht ersetzt**, sondern als zusätzliche Filterschicht
*danach* ansetzt: Er nutzt die von der bestehenden Pipeline bereits
berechneten Kennzahlen (Zyklusdauer, Positionsspanne, Anzahl Messwerte
je Signal, diverse Qualitätsmetriken) und ergänzt sie um neue,
begründete Schwellwerte sowie neu einzuführende Prüfschritte.

## Die vier Ebenen des Entscheidungsbaums

1. **Ebene 1 — Aufzeichnungssitzung.** Prüft, ob ein Zyklus zu einer
   gültigen, hinreichend langen Aufzeichnungssitzung gehört. Sehr kurze
   Sitzungen (z. B. Inbetriebnahme-Läufe oder abgebrochene Versuche)
   sind nicht repräsentativ für den Normalbetrieb und sollen die
   Baseline-Statistik nicht verzerren.
2. **Ebene 2 — Echter Zyklus: Stillstand- und Ausreißer-Ausschluss.**
   Prüft, ob ein erkannter Zyklus tatsächlich ein vollständiger,
   plausibler Bewegungshub ist: plausible Zyklusdauer innerhalb einer
   aus der Datenverteilung abgeleiteten Bandbreite, tatsächliches
   Erreichen des vollen Hubs und Rückkehr in die Ruhelage, eine zur
   erwarteten Abtastrate passende Anzahl an Messwerten des
   Referenzsignals, sowie — als zentrale neue Ergänzung — die explizite
   Stillstands-/Frozen-Signal-Prüfung (siehe unten).
3. **Ebene 3 — Multi-Sensor-Vollständigkeit.** Prüft, ob alle
   benötigten Sensorsignale im Zyklus überhaupt vorhanden sind und
   jeweils genügend Messwerte enthalten, um als vollständiger
   Merkmalsvektor für spätere Analysen/Modelle zu taugen.
4. **Ebene 4 — Signalqualität je Signal.** Prüft für jedes einzelne
   Signal innerhalb des Zyklus dessen interne Gesundheit: Wie groß ist
   der zeitliche Abdeckungsgrad des Signals über den Zyklus hinweg? Gibt
   es innerhalb des Zyklus ungewöhnlich große Zeitlücken? Enthält das
   Signal ungültige (nicht endliche) Werte? Zeigt ein eigentlich
   dynamisches Signal (z. B. Position, Geschwindigkeit, Strom) über den
   gesamten Zyklus hinweg überhaupt eine Veränderung, oder deutet ein
   konstanter Wert auf einen eingefrorenen Sensor hin?

Nur ein Zyklus, der alle vier Ebenen besteht, wird Teil des
„Pools nutzbarer Zyklen“ (siehe Kapitel 5).

## Abgrenzung: Segmentierungs-Parameter (Pipeline) vs. Prüfschritte der Zusatzschicht

Für die Beitragsabgrenzung ist entscheidend, dass nicht jedes der oben
genannten Kriterien Teil der neu entwickelten Filterschicht ist. Zwei
Kriterien — die Sitzungsgrenze (große Zeitlücke) und die Zyklusgrenze
(Positionsschwelle) — sind keine nachgelagerten Prüfungen, sondern
**Segmentierungs-Parameter**: Sie erzeugen die Aufzeichnungssitzungen
bzw. Bewegungszyklen überhaupt erst. Eine Änderung dieser Schwellwerte
bedeutet ein Neu-Segmentieren der Rohdaten und liegt damit in der
bestehenden Pipeline, nicht in der nachgelagerten Schicht (vgl. ADR-T01:
keine Reimplementierung der Pipeline).

Die Zusatzschicht enthält daher ausschließlich **Prüfschritte**, die
einen bereits geschnittenen Zyklus bewerten, ohne ihn neu zu
segmentieren. Für die beiden Segmentierungs-Parameter beschränkt sich der
Beitrag dieser Arbeit auf die datenbasierte **Neuherleitung** des
Schwellwerts samt Sicherheitsmarge (ADR-T06); die Anwendung des neuen
Werts erfolgt an der Quelle in der bestehenden Pipeline.

| Ebene | Segmentierungs-Parameter (Pipeline, geerbt) | Prüfschritt der Zusatzschicht (Beitrag dieser Arbeit) |
|---|---|---|
| 1 — Aufzeichnungssitzung | 1.1 Sitzungsgrenze bei großer Zeitlücke (`Lücke > 3600 s`) — Beitrag: Neuherleitung des Werts | 1.2 Mindest-Sitzungsgröße |
| 2 — Echter Zyklus | 2.1 Zyklusgrenze über Positionsschwelle (`Position > 1.0`) — Beitrag: Neuherleitung des Werts | 2.2 Plausible Zyklusdauer · 2.3 Voller Hub erreicht · 2.4 Erwartete Messwertzahl · 2.5 Stillstand-/Frozen-Signal-Prüfung |
| 3 — Multi-Sensor-Vollständigkeit | Definition der Core-/Optional-Signale (ADR-014, begründet) | 3.1 Präsenz-Gate (alle erforderlichen Signale vorhanden) · 3.2 Mindest-Messwerte je Signal |
| 4 — Signalqualität je Signal | — | 4.1 Abdeckungsgrad · 4.2 Keine großen Intra-Zyklus-Lücken · 4.3 Keine ungültigen Werte · 4.4 Kein eingefrorenes/konstantes Signal |

Auf jeder Ebene besitzt die Zusatzschicht somit ein eigenes
Bewertungs-Gegenstück zum jeweiligen Schnitt-Parameter: Der reine
Schnitt-Schwellwert verbleibt in der Pipeline, während die inhaltliche
Prüfung, ob der geschnittene Zyklus tatsächlich brauchbar ist, in der
Zusatzschicht erfolgt (z. B. Ebene 2: die Positionsschwelle schneidet den
Zyklus, aber ob der volle Hub tatsächlich erreicht wurde, prüft erst
Kriterium 2.3).

## Reifegradsystem für Kriterien

Ein zentrales methodisches Element dieser Arbeit ist, dass nicht nur
*welche* Kriterien geprüft werden, sondern auch, **wie gut jedes
einzelne Kriterium begründet ist**, explizit und einheitlich
klassifiziert wird. Dafür wird jedes Kriterium einem von fünf
Reifegraden zugeordnet:

- **Inkonsistent** — die Dokumentation widerspricht sich selbst über
  den Status eines Kriteriums (z. B. wird ein Schwellwert an einer
  Stelle als „endgültig freigegeben“ bezeichnet, an anderer Stelle im
  selben Projekt aber weiterhin als „vorläufig/experimentell“
  markiert). Ein solcher Widerspruch muss aufgelöst werden, bevor das
  Kriterium als verlässlich gelten kann.
- **Provisorisch** — das Kriterium existiert bereits im Code und wird
  angewendet, sein konkreter Schwellwert ist jedoch nicht aus einer
  Datenanalyse hergeleitet, sondern ursprünglich als plausibler
  Platzhalter gesetzt worden.
- **Nicht begründet** — das Kriterium bzw. sein Schwellwert ist
  konfiguriert und wird angewendet, aber es existiert keinerlei
  dokumentierte Herleitung, warum genau dieser Wert gewählt wurde
  (im Unterschied zu „provisorisch“ ist hier nicht einmal erkennbar,
  dass der Wert bewusst als Platzhalter gedacht war).
- **Strukturell** — das Kriterium prüft eine rein strukturelle
  Eigenschaft (z. B. „sind die Daten lückenlos aufeinanderfolgend“),
  ohne eine Aussage über die physikalische bzw. inhaltliche Qualität
  des Signals selbst zu treffen.
- **Begründet** — das Kriterium ist nachvollziehbar hergeleitet, entweder
  durch eine dokumentierte fachliche Entscheidung (z. B. Bestätigung
  durch die zuständigen Fachverantwortlichen) oder durch eine empirische
  Herleitung aus der beobachteten Datenverteilung mit Sicherheitsmarge.

Dieses Reifegradsystem erlaubt es, den Entscheidungsbaum nicht nur als
technische Filterkette zu präsentieren, sondern gleichzeitig **transparent
offenzulegen, wie belastbar jede einzelne Filterentscheidung ist** —
und macht sichtbar, an welchen Stellen noch fachliche Abstimmung oder
weitere Datenanalyse nötig ist, bevor ein Kriterium von einem niedrigeren
in einen höheren Reifegrad überführt werden kann.

## Geplante Stillstandsdefinition über ein Geschwindigkeitsfenster

Eine der wichtigsten neu eingeführten Prüfungen in Ebene 2 ist die
explizite **Stillstands-/Frozen-Signal-Erkennung**. Sie schließt die in
Kapitel 3 beschriebene Lücke, dass ein eingefrorenes oder de facto
unbewegtes Signal oberhalb des Bewegungsschwellwerts fälschlich als
gültiger, aktiver Zyklus gezählt werden könnte.

Der geplante Ansatz definiert Stillstand über ein gleitendes
Zeitfenster: Innerhalb jedes Fensters einer bestimmten Länge muss sich
entweder die Position um mehr als einen kleinen Mindestbetrag ändern,
oder — als physikalisch direkterer und damit bevorzugter Indikator —
der Betrag der Geschwindigkeit muss über einen kleinen Schwellwert
hinaus von null verschieden sein. Bleibt ein Fenster unterhalb beider
Kriterien, gilt der betroffene Abschnitt als Stillstand bzw.
eingefrorenes Signal und führt zur Ablehnung des Zyklus.

Die geschwindigkeitsbasierte Variante dieser Prüfung ist methodisch die
robustere, da eine Positionsschwelle „kleine Bewegung“ nicht zuverlässig
von „keine Bewegung“ unterscheiden kann, während die Geschwindigkeit
nahe null ein direkterer physikalischer Hinweis auf tatsächlichen
Stillstand ist. Die Umsetzung dieser Variante ist jedoch an eine Vorbedingung
geknüpft: Die physikalische Skalierung/Kalibrierung des
Geschwindigkeitssignals muss zunächst verifiziert werden, da sie in der
bestehenden Pipeline bislang nicht abschließend geprüft wurde. Bis diese
Verifikation vorliegt, wird die positionsbasierte Variante als
Übergangslösung verwendet, während die geschwindigkeitsbasierte Variante
als methodisch überlegene Zielarchitektur dokumentiert und vorbereitet
wird.
