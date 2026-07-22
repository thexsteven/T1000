# Fragen an die Testingenieure

Ziel: Alle Eingangswerte und Randbedingungen klären, um die Qualitäts-Checks (physikalische
Cross-Checks + neue Checks) korrekt zu implementieren, herzuleiten und begründen zu können.

Hinter jeder Frage steht **→ wofür** (welcher Check / welche Herleitung sie bedient).
**⭐ = kritisch** — ohne diese Antworten kann nicht gerechnet werden.

Wenn nur 10 Minuten Zeit sind, die ⭐-Fragen stellen: **1, 2, 3, 4, 9, 14, 16, 17, 25, 28.**
Die wichtigsten inhaltlichen Weichen sind **9, 16 und 25** — sie entscheiden, ob die Checks
nützen oder das Degradationssignal löschen.

---

## A — Hardware-Grundfakten (die vier Blocker)

- [ ] **1. ⭐** Was bedeutet der Positionswert **„84"** physikalisch — mm, % vom Vollhub oder Encoder-Counts? Wie lang ist der volle mechanische Hub? → *2.3, Einheit für alles Weitere*
- [ ] **2. ⭐** Was ist die **Nenngeschwindigkeit** / das Bewegungsprofil? Konstant oder trapezförmig (Beschleunigen / Fahren / Bremsen)? → *2.2, 2.5 (v_nom)*
- [ ] **3. ⭐** Was ist die **Abtastrate** der Messkette (Hz)? Fest oder variabel? → *2.4, 2.5 (Fensterbreite)*
- [ ] **4. ⭐** Hält der Aktuator an den **Endlagen** (oben/unten) kurz an? Wie lange nominal? → *2.5 — legitimer Stillstand am Umkehrpunkt darf nicht als Fehler zählen*
- [ ] **5.** Ist der Zyklus **symmetrisch** (Aus- und Einfahren gleich schnell) oder unterschiedlich? → *2.2, 2.5*
- [ ] **6.** Was ist die **0-Referenz** — der harte mechanische Anschlag, oder gibt es einen Offset? → *2.3 (min_pos ≤ 1)*
- [ ] **7.** Werden alle **8 Signale synchron** mit derselben Rate erfasst, oder pro Kanal unterschiedlich? → *2.4, Signalverständnis*

## B — Definition von „vollständiger Hub" / „ein Zyklus"

- [ ] **8.** Was ist **ein Zyklus** — ein volles Aus-und-Ein, oder eine Richtung? → *Grundlage 2.1–2.5*
- [ ] **9. ⭐** Gibt es legitime Testmodi mit **absichtlich kurzem / Teil-Hub** (z. B. Kurzhub-Dauertests)? → *falls ja, würde 2.3 sie fälschlich verwerfen — kritisch!*
- [ ] **10.** Trifft ein *gesunder* Aktuator immer exakt 84, oder sind z. B. 83,5 durch **Spiel / Verschleiß** normal? → *Toleranz für 2.3*
- [ ] **11.** Was bedeutet die Zyklus-Grenze **„position crosses 1.0"** physikalisch, und warum dieser Wert? → *2.1 Re-Herleitung*

## C — Sessions (Level 1)

- [ ] **12.** Was ist eine **„Aufnahme-Session"**? Wie lang ist die typische Pause zwischen zwei Testläufen? → *1.1 (warum 3600 s?)*
- [ ] **13.** Gibt es legitime **lange Pausen innerhalb eines Tests** (Mittag, Nacht-Hold), die fälschlich getrennt würden? → *1.1 Robustheit*
- [ ] **14. ⭐** Wie viele Zyklen produziert ein *echter* Testlauf mindestens? Woran erkennt man **Commissioning- / Abbruch-Läufe**? → *1.2 (Mindest-Session-Größe)*
- [ ] **15.** Gibt es bekannte **„Müll"-Sessions** (Kalibrierung, Inbetriebnahme), und sind die irgendwie markiert? → *1.2, Datenbereinigung*

## D — Freeze-Check (2.5, Kernstück)

- [ ] **16. ⭐** Stoppt der Aktuator im Normalbetrieb **jemals legitim mitten im Hub** (programmierte Zwischen-Halte, Positionshalte-Tests)? → *sonst flaggt 2.5 gültige Zyklen*
- [ ] **17. ⭐** Ist ein **Klemmen / Hängenbleiben mitten im Hub** ein realer Fehlerfall? Wodurch entsteht er (mechanisches Klemmen, Ansteuerung, Last)? → *rechtfertigt 2.5 überhaupt*
- [ ] **18.** Wie **kurz** kann ein realer, relevanter Stillstand sein? → *minimale Fensterbreite T*
- [ ] **19.** Wenn ein Sensor ausfällt: hält er den **letzten Wert** (flach) oder springt er auf 0 / NaN? → *echter Freeze vs. Sensor-Artefakt*
- [ ] **20.** Wird **Geschwindigkeit direkt gemessen** oder aus Position abgeleitet? → *ob der |v|-Check verlässlich ist*

## E — Sensoren & Signale

- [ ] **21.** Was sind die **8 Signale** genau, mit Einheiten und erwarteten Bereichen? → *Gesamtverständnis, Level 3/4*
- [ ] **22.** Welche sind die **Kern-Signale** für Gültigkeit vs. Hilfssignale (vib/temp scheinen ausgenommen)? → *bestätigt Level-4-Logik*
- [ ] **23.** **Rauschpegel / Auflösung** von Position und Geschwindigkeit? → *ε und δ müssen über dem Rauschen liegen*
- [ ] **24.** Bekannte **Sensor-Eigenheiten** — Dropouts, Quantisierung, Spikes? → *2.5 Robustheit*

## F — Was „schlecht" bedeutet (Degradationssignal schützen)

- [ ] **25. ⭐** Welche Auffälligkeiten sind **schlechte Daten** (rauswerfen) vs. **echtes, aber auffälliges Aktuator-Verhalten** (behalten — das ist das Verschleiß-Signal)? → *die zentrale Trennlinie der Arbeit*
- [ ] **26.** Wie sieht ein **verschlissener, aber funktionierender** Aktuator aus — im Gegensatz zu einem Datenfehler? → *dieselbe Trennlinie*
- [ ] **27.** Gibt es bekannte **Prüfstands- / Rig-Probleme** (loser Sensor, EMV), die Daten verfälschen? → *was die physischen Checks fangen sollen*

## G — Validierung (Beleg, dass 2.5 wirkt)

- [ ] **28. ⭐** Gibt es **gelabelte Beispiele** — Zyklen, von denen ihr *wisst*, dass sie kaputt sind (gestallt, unvollständig)? Auch nur eine Handvoll. → *Validierung des Ergebnis-Kapitels*
- [ ] **29.** Würde ein Ingenieur sich eine Auswahl der **geflaggten Zyklen ansehen** und bestätigen, dass sie wirklich fehlerhaft sind? → *Human-in-the-loop-Beleg*
- [ ] **30.** Gibt es **Test-Logs / Annotationen**, die vermerken, wann etwas schiefging? → *Ground Truth*

## H — Betriebsbedingungen

- [ ] **31.** Gibt es **verschiedene Testarten** (Dauerlauf, Performance, Charakterisierung) mit unterschiedlicher Zyklusform / -dauer? → *ein fester Schwellensatz passt evtl. nicht auf alle*
- [ ] **32.** Ändern **Temperatur / Last** die Nenndauer / -geschwindigkeit? → *Toleranz für 2.2*

---

## Nach dem Gespräch — was sich daraus rechnen lässt

Sobald die Antworten da sind, ergeben sich die Schwellen direkt:

- **2.2 Dauer:** `t_nom = 2 × Hublänge / Nenngeschwindigkeit (+ Verweilzeit)` → Fenster = `t_nom ± Toleranz`
- **2.3 Full stroke:** `84` = mechanischer Endanschlag (aus Datenblatt), Toleranz aus Frage 10
- **2.4 Sample-Anzahl:** `Abtastrate × Dauer` (Konsistenz-Check, kein unabhängiger Beweis)
- **2.5 Freeze:** `v_nom = Hublänge / Halbzyklus-Zeit`; `ε` = wenige % von `v_nom` (über Rauschen, Frage 23); `T` aus Frage 18; Umkehrpunkte aus Frage 4 ausklammern
