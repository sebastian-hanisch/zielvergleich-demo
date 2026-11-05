# Dasselbe Problem, drei Ziele – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-zielvergleich-demo.streamlit.app/)** -->

Stück 1 der Linie **Zielfunktionsdesign** („Das Ziel ist das Modell“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (Arbeitsname; Name, Bereich und Themenfeld werden erst bei der Einbindung in die Website festgelegt). Es ist die **Wurzel** der Linie: dieselbe Instanz, derselbe Löser, nur das Ziel wechselt. Das Beispiel: **n Personen übernehmen n Aufgaben**, jede Paarung hat eine Belastung; ein Plan ordnet jeder Person eine Aufgabe zu, und ein Ziel macht aus den Belastungen eine Zahl. Alles ist **simuliert**; keine Aussage über echte Personen, Betriebe oder Lasten.

## Warum dieses Problem

Welches Ziel man optimiert, entscheidet, welche Lösung man bekommt. Die Demo zeigt das an der kleinsten Aufgabe, an der es sich vollständig zeigen lässt: Bis acht Personen werden **alle Pläne aufgezählt** (8! = 40 320), darüber rechnen die Ungarische Methode (Summe, Quadratsumme) und ein Engpassverfahren (Maximum) das Optimum **exakt**. Die Kernfrage: Wandert das Optimum, wenn nur das Ziel wechselt, und wovon hängt das ab?

## Modell

Gegeben Belastungen `c[i][j]` (Zeile Person, Spalte Aufgabe). Ein Plan ist eine Permutation `π`; Person `i` trägt `b_i = c[i][π(i)]`. Ziele: **Summe** `Σ b_i`, **Quadratsumme** `Σ b_i²`, **Maximum** `max b_i`, allgemein `Σ b_i^p` (p = 1 ist die Summe, p = 2 die Quadratsumme, p → ∞ das Maximum). Gleichstandsregeln (sichtbar, siehe unten): beim Maximum erst das kleinste Maximum, dann die kleinste Summe, dann der kleinste Plan; bei Summe und Quadratsumme der erste Plan in der Reihenfolge von `itertools.permutations` (aufgezählt) beziehungsweise ein beliebiger gleichwertiger Plan (Löser). Formeln und Lösungsweg stehen im 📐-Expander der App.

## Methodik

Drei Instanzfamilien: **ganze Zahlen 1 bis 9** (viele Gleichstände), **gleichverteilt 0 bis 100**, **mit Personeneffekt** (manche Personen sind systematisch stärker belastet). Die App zeigt: die Belastungsmatrix mit den drei gewählten Plänen, die Belastung je Person unter den drei Plänen, alle Pläne als Punktwolke (Summe gegen Maximum), den p-Regler und die Häufigkeiten über 20 feste Instanzen. Verdikte entstehen live aus der Rechnung, jede Zahl im Text kommt aus dem Ergebnis.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stammen aus den Auswertungsfunktionen der App und sind in `tests/test_claims.py` nachgerechnet. „Je 20 feste Instanzen“ heißt `SWEEP_SEEDS` (Seeds 100000 bis 100019), nie ein einzelner Seed; die Zahlen sind **Anzahlen von Instanzen**, kein Satz und keine Aussage über andere Instanzen.

| Frage | Befund |
|---|---|
| Handbeispiel (n = 4, ganze Zahlen, Seed 358; 24 Pläne) | Drei verschiedene eindeutige Optima: **Summe 14** (Belastungen 7, 3, 2, 2), **Quadratsumme 65** mit Summe 15 (6, 3, 2, 4), **Maximum 5** mit Summe 16 (5, 3, 4, 4); über p = 1 bis ∞ gibt es 3 verschiedene Optimalpläne |
| Wie oft ist das Quadrat-Optimum in der Summe so gut wie das Summen-Optimum? (Je 20 Instanzen; n = 4 / 6 / 8) | gleichverteilt **16 / 14 / 10**, mit Personeneffekt **16 / 12 / 11**, ganze Zahlen **19 / 20 / 17**: Quadrat statt Summe ändert die Summe in der Minderheit der Instanzen, bei gleichverteilten Belastungen mit wachsendem n häufiger |
| Alle drei Optima gleichwertig in der Summe (n = 4 / 6 / 8) | gleichverteilt **14 / 13 / 5**, mit Personeneffekt **11 / 8 / 4**, ganze Zahlen **18 / 20 / 17** |
| Maximum nicht eindeutig, mehr als ein bester Plan (n = 4 / 6 / 8) | gleichverteilt **4 / 13 / 17**, mit Personeneffekt **11 / 19 / 18**, ganze Zahlen **7 / 20 / 19**: beim Maximum sind Gleichstände die Regel, weil nur ein einziger Eintrag zählt |
| Quadrat-Optimum mit größerem Maximum als das Summen-Optimum (n = 4 / 6 / 8) | gleichverteilt **0 / 0 / 0**, mit Personeneffekt **0 / 2 / 0**, ganze Zahlen **0 / 0 / 0**: selten, aber möglich (Preset „Quadrat verschlechtert das Maximum“: Maximum 44,1 im Summen-Plan gegen 47,6 im Quadrat-Plan) |
| Die Summe des Optimums sinkt irgendwo mit wachsendem p (n = 4 / 6 / 8) | gleichverteilt **1 / 4 / 5**, mit Personeneffekt **3 / 6 / 10**, ganze Zahlen **0 / 0 / 1**: der „Preis“ eines faireren Ziels wächst nicht gleichmäßig |
| Preset „Gleichstand beim Maximum“ (n = 6, ganze Zahlen, Seed 175) | **96** von 720 Plänen haben das kleinste Maximum 8; die Summe entscheidet; Summe 18 in allen drei Plänen, Quadratsumme 92 / 90 / 92 |
| Preset „Viele Personen“ (n = 60, Personeneffekt, Seed 3; Löser statt Aufzählung) | Summe 1882,9 im Summen-Plan, 1903,4 im Quadrat-Plan, 1899,8 im Maximum-Plan; Maximum 51,3 / 46,3 / 44,6: der Maximum-Plan hat hier die kleinere Summe als der Quadrat-Plan |

## Ehrliche Grenzen

- **Instanzfamilien, nicht die Welt:** Die Befunde gelten für drei synthetische Familien kleiner Zuordnungen. Wie oft Ziele den Plan wechseln, hängt an der Familie; echte Belastungen können sich anders verhalten.
- **Gleichstandsregeln gestalten das Ergebnis:** Beim Maximum entscheidet die zweite Regel (kleinste Summe) mit; ohne sie wäre die Wahl willkürlich. Die Folgen für den „Preis“ eines fairen Ziels sind Stoff eines späteren Stücks der Linie.
- **Bis n = 8 aufgezählt, darüber Löser:** Das Bild aller Pläne gibt es nur bis n = 8; die Löser sind gegen die Aufzählung geprüft (siehe Verifikation), aber die Optimalmenge beim Maximum zählt die Demo nur aufgezählt.
- **Das Ziel ist gegeben:** Welches Ziel gelten soll, ist eine Entscheidung, die die Demo nicht trifft; sie zeigt nur, was ein Wechsel ändert.
- **Keine Literaturaussage:** Alle Zahlen sind Messungen an diesen Familien; die Demo behauptet nichts über andere Instanzen.

## Verifikation

Insgesamt 79 Tests (`pytest tests/`), alle grün.

- **Kern:** Optima gegen das Handbeispiel von Hand (24 Pläne, drei verschiedene eindeutige Optima), gegen reines Python (itertools, ohne numpy) und gegen `scipy.optimize.linear_sum_assignment`; Löser (Ungarische Methode, Schwellwertsuche mit Matching) gegen die Aufzählung bis n = 7 und gegen reines Python bis n = 6; unabhängiger Zulässigkeitsprüfer; Randfälle (n = 1, n = 2, alle Einträge gleich, viele Gleichstände, Seed 0, n = 200).
- **Eigenschaften:** Zeilen- und Spaltenpermutation, Skalierung (Summe und Maximum linear, Quadratsumme quadratisch), Zeilenkonstante ändert den Summen-Plan nicht, lexikographische Wahl hat die kleinste Summe unter allen Plänen mit dem kleinsten Maximum.
- **Verdikte:** reine Funktionen, jede Verzweigung und jede Zahl im Text an handgesetzten Werten (`tests/test_verdicts.py`).
- **Presets:** Vollständigkeit, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, und dass jedes Preset zeigt, was sein Name sagt (`tests/test_presets.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum, n = 200), Footer-Test, Layout (Schnellstart in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Änderung eines Reglers hebt die Markierung auf).
- **Claims:** jede Zahl dieser README in `tests/test_claims.py`.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `zvg_algorithm.py` | Kern: Aufzählung, Ungarische Methode, Engpassverfahren, Zulässigkeitsprüfer |
| `zvg_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `zvg_evaluation.py` | Kennzahlen, Verdikte, Sweeps über feste Instanzen |
| `zvg_layout.py` | Fester Kopf (Stylesheet) |
| `zvg_pdf_export.py` | PDF-Export des Ergebnisses |
| `zvg_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `zvg_scenario.py` | Instanzen (drei Familien) |
| `zvg_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handbeispiel, Gegenproben, Randfälle, Verdikte, Presets, Claims, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe, Orakel |

## Bewusst nicht umgesetzt

- **Kein Preis der Fairness:** Wie viel Summe das faire Ziel kostet und wie das mit n wächst, zeigt ein eigenes Stück der Linie.
- **Keine Pareto-Front, keine Gewichtssumme:** Zwei Kriterien und die Frage, welche Kompromisse eine Gewichtssumme erreicht, sind ein eigenes Stück.
- **Keine lexikographischen Ziele mit Gewicht:** Hier gilt die Regel „erst Maximum, dann Summe“ nur als sichtbare Gleichstandsregel; ihre Tücken (Gewicht, Toleranz, Gleitkomma) sind ein eigenes Stück.
- **Keine Strafterme, keine Scoring-Regeln, keine Ersatzziele:** spätere Stücke der Linie.
- **Keine Literatur- oder Gleichgewichtsaussagen:** keine α-Familie der Fairness als Behauptung.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
