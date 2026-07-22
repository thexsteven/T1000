# 4. Entscheidungsbaum und Kriterien-Reifegradsystem

## Grundidee

Die bestehende Pipeline validiert und verwirft Zyklen seit V2.1 bereits
selbst — datengetrieben und statistisch (Kapitel 3, Stufen 9–10). Was sie
**nicht** leistet, ist eine absolute, populationsunabhängige
**physikalische** Beurteilung der Brauchbarkeit, die
In-Zyklus-Stillstandsprüfung und eine transparente Aussage darüber, *wie
belastbar* jedes einzelne Qualitätskriterium — auch die der Pipeline —
überhaupt begründet ist. Um genau diese verbleibenden Lücken (Kapitel 3)
zu schließen, wird ein **mehrstufiger Entscheidungsbaum** entwickelt.

Er beantwortet für jeden bereits statistisch validierten Bewegungszyklus
die ergänzende Frage: „Ist dieser Zyklus *physikalisch* überhaupt
brauchbar — voller Hub, tatsächlich in Bewegung, plausibel — und wenn
nicht, warum nicht?“ Ein Zyklus muss dabei alle Ebenen des Baums von oben
nach unten bestehen; scheitert er an einer Ebene, wird er mit einem
dokumentierten Ablehnungsgrund aus dem Pool ausgeschlossen, aber nicht
stillschweigend verworfen — jede Ablehnung bleibt nachvollziehbar
protokolliert (vgl. ADR-T07).

Der Baum ist bewusst so aufgebaut, dass er die bestehende Pipeline aus
Kapitel 3 **weder ersetzt noch ihre statistische Validierung
wiederholt**, sondern als physikalischer Querschnitt *auf* ihr ansetzt:
Er nutzt die von der Pipeline bereits berechneten Kennzahlen (Zyklusdauer,
Positionsspanne, Anzahl Messwerte je Signal, diverse Qualitätsmetriken)
sowie deren validierte Zyklusklassen und ergänzt sie um (a) einen
**absoluten physikalischen** Boden dort, wo die Pipeline nur *relativ zur
Population* prüft, (b) die beiden Prüfungen, die der Pipeline ganz fehlen
(In-Zyklus-Stillstand, Mindest-Sitzungsgröße), und (c) eine
**Reifegrad-Bewertung** jedes Kriteriums — der pipeline-eigenen
eingeschlossen.

## Die vier Ebenen des Entscheidungsbaums

Die Kriterien sind in vier Ebenen organisiert. Viele der numerischen
Grenzen werden inzwischen von der statistischen Validierung der Pipeline
(Stufen 9–10) durchgesetzt; der Baum ergänzt an diesen Stellen den
absoluten physikalischen Querschnitt und fügt die fehlenden Prüfungen
hinzu.

1. **Ebene 1 — Aufzeichnungssitzung.** Prüft, ob ein Zyklus zu einer
   gültigen, hinreichend langen Aufzeichnungssitzung gehört. Die
   Sitzungsgrenze selbst ist ein Segmentierungs-Parameter der Pipeline
   (diese Arbeit leitet nur den Wert neu her); die **Mindest-Sitzungsgröße**
   ist eine genuin neue Prüfung: Sehr kurze Sitzungen (z. B.
   Inbetriebnahme-Läufe oder abgebrochene Versuche) sind nicht
   repräsentativ für den Normalbetrieb und sollen die Baseline-Statistik
   nicht verzerren.
2. **Ebene 2 — Echter Zyklus: Stillstand- und Ausreißer-Ausschluss.**
   Prüft, ob ein erkannter Zyklus tatsächlich ein vollständiger,
   plausibler Bewegungshub ist. Die numerischen Bandbreiten für
   Zyklusdauer, vollen Hub und Messwertzahl werden von der Pipeline
   **statistisch** durchgesetzt; diese Arbeit ergänzt sie um eine
   **absolute physikalische** Untergrenze, die nicht mit der Population
   mitwandert, sowie — als zentrale genuin neue Ergänzung — die explizite
   **In-Zyklus-Stillstands-/Frozen-Signal-Prüfung** (siehe unten).
3. **Ebene 3 — Multi-Sensor-Vollständigkeit.** Prüft, ob alle benötigten
   Sensorsignale im Zyklus überhaupt vorhanden sind und jeweils genügend
   Messwerte enthalten, um als vollständiger Merkmalsvektor für spätere
   Analysen/Modelle zu taugen. Diese Prüfungen werden inzwischen von der
   Pipeline abgedeckt (`valid_core_cycle`); der Baum bildet sie als Ebene
   ab, um sie mit einem Reifegrad zu versehen und lückenlos in die
   Ablehnungslogik einzuordnen.
4. **Ebene 4 — Signalqualität je Signal.** Prüft für jedes einzelne
   Signal innerhalb des Zyklus dessen interne Gesundheit: Wie groß ist der
   zeitliche Abdeckungsgrad des Signals über den Zyklus hinweg? Gibt es
   ungewöhnlich große Intra-Zyklus-Zeitlücken? Enthält das Signal
   ungültige (nicht endliche) Werte? Zeigt ein eigentlich dynamisches
   Signal (Position, Geschwindigkeit, Strom) über den *gesamten* Zyklus
   überhaupt eine Veränderung? Auch diese Prüfungen liegen als
   statistische bzw. harte Regeln bei der Pipeline; der dort nicht
   erfassbare Fall eines nur *abschnittsweise* eingefrorenen Signals wird
   durch die In-Zyklus-Prüfung in Ebene 2 abgedeckt.

Ein Zyklus wird Teil des „Pools nutzbarer Zyklen“ (siehe Kapitel 5),
wenn er **sowohl** die statistische Validierung der Pipeline **als auch**
den physikalischen Boden dieser Arbeit besteht.

## Abgrenzung: Wer prüft was (Segmentierung · Statistik · Physik · Neu)

Für die Beitragsabgrenzung ist entscheidend, dass nicht jedes der oben
genannten Kriterien Teil des Beitrags dieser Arbeit ist. Seit V2.1
verteilen sich die Kriterien auf vier Eigentümer-Kategorien:

- **Pipeline · Segmentierung** — ein Schwellwert, der Sitzungen/Zyklen
  überhaupt erst *erzeugt*; er liegt oberhalb der Regelgenerierung
  (Stufe 9) in der Pipeline. Eine Änderung bedeutet ein Neu-Segmentieren
  der Rohdaten; diese Arbeit leitet nur den Wert datenbasiert neu her
  (ADR-T06) und reimplementiert die Segmentierung nicht (ADR-T01).
- **Pipeline · statistisch** — inzwischen durch die datengetriebenen
  Regeln der Pipeline (Stufen 9–10) relativ zur Population durchgesetzt.
- **Diese Arbeit · physikalisch** — ein *absoluter* physikalischer
  Querschnitt zusätzlich zur statistischen Regel (ADR-T02).
- **Diese Arbeit · neu** — eine Prüfung, die die Pipeline gar nicht
  besitzt.

| Ebene | Kriterium | Eigentümer |
|---|---|---|
| 1 | 1.1 Sitzungsgrenze bei großer Zeitlücke (`Lücke > 3600 s`) | Pipeline · Segmentierung (Wert neu hergeleitet) |
| 1 | 1.2 Mindest-Sitzungsgröße | Diese Arbeit · neu |
| 2 | 2.1 Zyklusgrenze über Positionsschwelle (`Position > 1.0`) | Pipeline · Segmentierung (Wert neu hergeleitet) |
| 2 | 2.2 Plausible Zyklusdauer | Pipeline · statistisch + Diese Arbeit · physikalisch |
| 2 | 2.3 Voller Hub erreicht | Pipeline · statistisch + Diese Arbeit · physikalisch |
| 2 | 2.4 Erwartete Messwertzahl | Pipeline · statistisch + Diese Arbeit · physikalisch |
| 2 | 2.5 In-Zyklus-Stillstand-/Frozen-Signal-Prüfung | Diese Arbeit · neu |
| 3 | 3.1 Alle erforderlichen Signale vorhanden | Pipeline · statistisch (`valid_core_cycle`) |
| 3 | 3.2 Mindest-Messwerte je Signal | Pipeline · statistisch |
| 4 | 4.1 Abdeckungsgrad des Zyklus | Pipeline · statistisch |
| 4 | 4.2 Keine großen Intra-Zyklus-Lücken | Pipeline · statistisch |
| 4 | 4.3 Keine ungültigen (nicht endlichen) Werte | Pipeline · statistisch (harte Regel) |
| 4 | 4.4 Kein über den ganzen Zyklus eingefrorenes/konstantes Signal | Pipeline · statistisch (ganzer Zyklus) · abschnittsweise → 2.5 |

Der genuine Beitrag dieser Arbeit sind damit die **neuen** Prüfungen
(In-Zyklus-Stillstand 2.5, Mindest-Sitzungsgröße 1.2), die **absoluten
physikalischen** Querschnitte in Ebene 2, die **Neuherleitung** der beiden
Segmentierungs-Schwellwerte (1.1, 2.1) sowie die Reifegrad-Bewertung über
*alle* Kriterien. Der reine Schnitt-Schwellwert verbleibt in der Pipeline,
ebenso die statistische Validierung; die Frage, ob der geschnittene Zyklus
*physikalisch* brauchbar ist, beantwortet erst der Baum (z. B. Ebene 2:
die Positionsschwelle schneidet den Zyklus, aber ob der volle Hub
tatsächlich erreicht wurde, prüft physikalisch erst Kriterium 2.3 —
während die Pipeline dieselbe Größe nur statistisch gegen die Population
prüft).

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

Es gilt ausdrücklich **auch für die inzwischen implementierten
statistischen Regeln der Pipeline** — einschließlich ihres eigenen
`provisional`-Flags aus der Regelgenerierung (Stufe 9) — und liefert so
eine einheitliche Vertrauensbewertung über beide Arbeiten hinweg
(vgl. ADR-T04).

## Geplante Stillstandsdefinition über ein Geschwindigkeitsfenster

Eine der wichtigsten neu eingeführten Prüfungen in Ebene 2 ist die
explizite **In-Zyklus-Stillstands-/Frozen-Signal-Erkennung**. Sie
schließt die in Kapitel 3 beschriebene Lücke, dass ein eingefrorenes oder
de facto unbewegtes Signal oberhalb des Bewegungsschwellwerts
fälschlich als gültiger, aktiver Zyklus gezählt werden könnte — ein Fall,
den die `constant_signal`-Prüfung der Pipeline nicht erfasst, weil sie
nur über den *gesamten* Zyklus konstante Signale erkennt.

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
wird (vgl. ADR-T05).
