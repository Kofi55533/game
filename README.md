# Trading-Agenten systematisch optimieren

> **API-Key einrichten:** Wer nur eine nicht bearbeitbare Dateivorschau und kein
> Terminal sieht, kann dort keinen Key eingeben. Die genaue Navigation für ein
> GitHub-Actions-Repository-Secret steht in
> [`API_KEY_EINRICHTEN.md`](API_KEY_EINRICHTEN.md).
> Der technische Secret-Name lautet exakt `MODEL_API_KEY`; nach dem Anlegen ist
> ein neuer Workflow-Lauf beziehungsweise ein vollständig neuer Task
> erforderlich. Eine weitere Nachricht im laufenden Chat lädt das Secret nicht
> nach.
> **Wichtig:** Der manuelle GitHub-Knopf **Run workflow** erscheint erst, wenn
> die Workflow-Datei in den Standard-Branch gemergt wurde.

Dieses Repository dient als Ausgangspunkt für reproduzierbare Experimente mit
einem oder mehreren Trading-Agenten. Ziel ist **nicht**, die beste historische
Rendite zu finden, sondern belastbar zu prüfen, welcher Agent unter welchen
Marktbedingungen nach Kosten und Risiko einen Vorteil hat.

> **Hinweis:** Das Projekt ist ein Forschungs- und Testaufbau und keine
> Anlageberatung. Ergebnisse aus Backtests sind keine Garantie für zukünftige
> Ergebnisse.

## 1. Zuerst eine messbare Forschungsfrage formulieren

Jeder Versuch sollte vor dem Lauf festhalten:

- **Markt und Instrumente:** zum Beispiel liquide Aktien, Futures oder Krypto;
- **Zeitraum und Frequenz:** etwa Tagesdaten von 2015–2025 oder Stundenkerzen;
- **Entscheidung:** Long/Flat, Long/Short oder Portfolio-Gewichte;
- **Handelsrestriktionen:** Positionslimits, Hebel, Mindesthaltedauer und
  Liquiditätsgrenzen;
- **Kostenmodell:** Gebühren, Spread, Slippage, Finanzierung und Market Impact;
- **Vergleichsmaßstab:** Buy-and-Hold, gleichgewichtetes Portfolio oder eine
  einfache regelbasierte Strategie;
- **Erfolgskriterium:** beispielsweise höhere risikobereinigte Rendite bei
  begrenztem Drawdown und stabilen Ergebnissen außerhalb der Trainingsdaten.

Eine geeignete erste Hypothese ist: „Agent A erzielt in Trendphasen nach allen
Kosten eine höhere Sortino Ratio als die Benchmark, ohne den maximalen Drawdown
um mehr als fünf Prozentpunkte zu erhöhen.“

## 2. Empfohlene Projektstruktur

```text
configs/              # Versionierte Daten-, Agenten- und Experimentparameter
data/raw/             # Unveränderte Quelldaten (nicht in Git einchecken)
data/processed/       # Punkt-in-Zeit bereinigte Features
src/data/             # Import, Validierung und Feature-Berechnung
src/env/              # Marktumgebung, Ausführung und Kostenmodell
src/agents/            # Einheitliche Agentenschnittstelle und Implementierungen
src/backtest/          # Walk-forward-Läufe und Portfolio-Buchhaltung
src/evaluation/        # Kennzahlen, Regimeanalyse und statistische Tests
tests/                 # Unit-, Integrations- und Regressionstests
artifacts/             # Reports, Modelle und Lauf-Metadaten (meist nicht in Git)
```

Jeder Agent sollte dieselbe Schnittstelle verwenden: Er erhält ausschließlich
zu diesem Zeitpunkt verfügbare Beobachtungen und liefert eine Zielposition oder
Portfolio-Gewichte. Ausführung, Risiko- und Kostenlogik gehören in die Umgebung,
nicht in den Agenten. So bleiben Vergleiche fair.

## 3. Festgelegter Startumfang

Für den **ersten historischen Prototyp sind keine Börsen-API-Keys nötig**. Der
Backtester kann zunächst mit heruntergeladenen CSV-/Parquet-Dateien oder einem
öffentlichen Market-Data-Endpunkt arbeiten. Statt vorab eine einzelne Variante
auszuwählen, ist der Startumfang nun als versionierte Experimentmatrix in
`configs/experiment.toml` festgelegt:

- Bybit als erste Venue, ohne die Architektur auf Bybit festzulegen;
- Spot und lineare Perpetuals;
- 1 Minute, 15 Minuten, 1 Stunde und 1 Tag;
- Buy/Sell/Hold, Zielposition und Portfoliogewichte;
- Long-only und – wo das Instrument es erlaubt – Long/Short;
- 1x, 2x, 3x und 5x Leverage;
- vier Jahre Historie und ein aggressives Forschungs-Risikoprofil;
- alle **zum jeweiligen historischen Zeitpunkt geeigneten** USD-, USDT- und
  USDC-Paare statt einer heute festgelegten Coin-Liste.

„Alle testen“ bedeutet dabei nicht, jede mögliche Kombination sofort teuer zu
trainieren. Der reproduzierbare Plan testet zuerst 36 Varianten bei 1x Leverage.
Erst die Risiko-Stufe erweitert Perpetual-Varianten auf 2x, 3x und 5x und enthält
108 Konfigurationen. Walk-forward-Fenster und mehrere Seeds befinden sich
innerhalb jeder Konfiguration. So bleibt der Suchraum messbar und Selection Bias
wird reduziert, ohne eine gewünschte Modell- oder Frequenzklasse vorab
auszuschließen.

Die Matrix kann ohne Installation angezeigt werden:

```bash
PYTHONPATH=src python -m tradinglab.cli --stage screening --count
PYTHONPATH=src python -m tradinglab.cli --stage risk --count
PYTHONPATH=src python -m tradinglab.cli --stage screening
```

Der erste implementierte Durchstich sollte anschließend in dieser Reihenfolge
entstehen:

1. öffentliche historische Bybit-Daten lokal importieren und validieren;
2. daraus marktweite und instrumentspezifische Features zeitkorrekt berechnen;
3. eine einheitliche `observe -> decide -> execute`-Schnittstelle bauen;
4. den Agenten und zwei einfache Baselines über dieselben Zeitfenster laufen lassen;
5. Kosten-, Leakage- und Buchhaltungstests ausführen;
6. Walk-forward- und Regimebericht erzeugen;
7. erst nach einem belastbaren Backtest einen Testnet-/Paper-Trading-Adapter
   ergänzen.

### Wann API-Keys erforderlich werden

| Aufgabe | Schlüssel nötig? | Empfohlener Zugriff |
| --- | --- | --- |
| Lokaler Backtest aus Dateien | Nein | keiner |
| Abruf öffentlicher Kurse | häufig nein | öffentlicher, nur lesender Endpunkt |
| Höhere Datenlimits/premium Historie | je nach Anbieter | separater Data-only-Key |
| Kontostand im Paper Trading | ja | Read + Testnet, keine Auszahlungen |
| Orders im Testnet | ja | Trade nur im Testnet |
| Echtes Trading | später | eigener, eng begrenzter Produktions-Key |

Geheimnisse werden niemals in Git, Konfigurationsdateien, Logs oder Prompts
gespeichert. Falls später ein Key notwendig ist, wird nur sein Name – etwa
`EXCHANGE_API_KEY` – in einer `.env.example` dokumentiert; der Wert bleibt in
einer lokalen Umgebungsvariable oder einem Secret Manager. Auszahlungsrechte
bleiben deaktiviert, Keys werden je Umgebung getrennt und nach Möglichkeit auf
IP-Adressen sowie minimale Rechte beschränkt.

### Wo der Modell-API-Key eingetragen wird

Der Modell-Key wird **nicht in den Chat und nicht in `.env.example` kopiert**.
`.env.example` ist nur die versionierte Vorlage. Sie wird als `.env` kopiert;
nur in dieser nicht versionierten Kopie wird der echte Key eingetragen:

```bash
cd /workspace/game
cp .env.example .env
chmod 600 .env
```

Anschließend wird `.env` lokal mit einem Editor ausgefüllt:

```dotenv
MODEL_API_KEY=hier_lokal_eintragen
```

Ohne bearbeitbare Dateien wird in der Secret-Verwaltung ein Eintrag namens
`MODEL_API_KEY` angelegt. Die vollständige Anleitung steht in
[`API_KEY_EINRICHTEN.md`](API_KEY_EINRICHTEN.md).

Da das Projekt ohne zusätzliche Dotenv-Abhängigkeit auskommt, werden die Werte
vor dem Prozess in die Umgebung geladen:

```bash
set -a
source .env
set +a
PYTHONPATH=src python -m tradinglab.secrets
```

Der Prüf-Befehl gibt ausschließlich `true` oder `false` für vorhandene Werte
aus. Er zeigt den Schlüssel weder vollständig noch teilweise an. Die echte
`.env` wird durch `.gitignore` ausgeschlossen; nur die leere `.env.example`
wird versioniert.

Bybit-Schlüssel bleiben leer, solange nur öffentliche historische Daten geladen
werden. Für einen späteren privaten Testnet-Adapter stehen getrennt
`BYBIT_API_KEY` und `BYBIT_API_SECRET` bereit. Ein Live-Key mit
Auszahlungsberechtigung darf hier nicht verwendet werden.

### Was der historische Test ungefähr kostet

Ein Backtest ist nicht „ein API-Call“. Kurs-APIs liefern üblicherweise nur eine
begrenzte Zahl Kerzen pro Antwort; vier Jahre Minutendaten müssen daher über
viele Seiten abgerufen werden. Die Marktdaten werden **einmal heruntergeladen,
lokal gespeichert und danach für alle Experimente wiederverwendet**. Aus den
Minutendaten werden 15-Minuten-, Stunden- und Tageskerzen lokal erzeugt. Dadurch
bezahlen wir weder Daten noch Downloadzeit für jede der 36 beziehungsweise 108
Varianten erneut.

Der mitgelieferte Rechner macht die Annahmen sichtbar:

```bash
PYTHONPATH=src python -m tradinglab.cost --symbols 100
```

Bei 100 Symbolen, vier Jahren und angenommenen 1.000 Kerzen pro Datenseite ergibt
das grob 210 Millionen Minutekerzen, rund 210.400 öffentliche Datenanfragen und
etwa 12,5 GiB kompakte Binärdaten. CSV-Dateien können deutlich größer sein. Die
tatsächliche Laufzeit hängt vom zulässigen Rate Limit, von Datenlücken und von
der Parallelisierung ab. Die Rechnung ist eine Kapazitätsschätzung, keine
Zusicherung eines aktuellen Bybit-Limits oder -Preises.

Öffentliche Kursabfragen verursachen in unserem Kostenmodell zunächst **0 USD
direkte API-Kosten**. Serverzeit, Speicher und Netzwerk können trotzdem kosten.
Für einen deterministischen lokalen Agenten entstehen ebenfalls keine
Modell-API-Kosten. Falls der Agent bei jeder Entscheidung ein kostenpflichtiges
Sprachmodell aufruft, wären dagegen Millionen einzelner Entscheidungen zu teuer.
Dann werden Modellaufrufe nur für ausgewählte Zustände beziehungsweise gebündelte
Entscheidungen eingesetzt und unveränderliche Ergebnisse gecacht.

Ein konkreter Modellpreis wird nicht im Code fest verdrahtet. Er kann mit den
aktuellen Preisen des verwendeten Anbieters eingesetzt werden:

```bash
PYTHONPATH=src python -m tradinglab.cost \
  --symbols 100 \
  --input-tokens 1000 \
  --output-tokens 100 \
  --input-usd-per-million PREIS \
  --output-usd-per-million PREIS
```

Damit trennen wir drei Kostenarten sauber: öffentliche Datendownloads,
Rechen-/Speicherkosten und optionale Modell-Tokens. Für den nächsten Schritt
werden weder ein Bybit-Key noch ein anderer privater API-Key benötigt.

## 4. Welchen Marktüberblick der Agent erhalten sollte

Ja: Beim Handel einer einzelnen Kryptowährung sollte der Agent optional sehen können,
wie sich der **übrige Markt** verhält. Dafür ist kein einzelner magischer
Datenpunkt ausreichend. Statt alle Rohkurse ungefiltert in den Agenten zu geben,
wird zu jedem Entscheidungszeitpunkt ein kompakter, kausal berechneter
Marktzustand erzeugt.

### Beobachtung für ein Instrument

Für Coin `i` zum Zeitpunkt `t` kann der Agent vier Informationsblöcke erhalten:

```text
observation(i, t) = [
  eigene_features(i, t),
  markt_features(t),
  relative_features(i, t),
  portfolio_zustand(t)
]
```

**Eigene Features** sind beispielsweise Renditen über mehrere Horizonte,
Volatilität, Volumenänderung, Spread und Momentum des betrachteten Coins.

**Marktweite Features** können enthalten:

- Rendite und Volatilität eines marktwertgewichteten Kryptoindex;
- gleichgewichtete Rendite des zum Zeitpunkt `t` handelbaren Universums;
- Anteil der Coins mit positiver Rendite („Market Breadth“);
- Anteil oberhalb eines gleitenden Durchschnitts;
- aggregiertes Volumen und dessen Veränderung;
- Median-Rendite sowie Streuung der Coin-Renditen;
- mittlere rollierende Korrelation und erster PCA-Faktor;
- Bitcoin-/Ethereum-Rendite und -Dominanz, sofern zeitkorrekt verfügbar;
- Anteil Stablecoins beziehungsweise Stablecoin-Depeg-Indikatoren;
- marktweite Liquidations- oder Funding-Merkmale, falls die Daten zuverlässig
  historisiert werden können.

**Relative Features** beschreiben genau den angesprochenen Bezug eines Coins zum
Gesamtmarkt:

- Überschussrendite des Coins gegenüber Index und Median;
- rollierendes Beta und rollierende Korrelation zum Markt;
- relatives Momentum und relatives Volumen;
- Rang oder Perzentil innerhalb aller Coins;
- coin-spezifische Residualrendite nach Abzug des Marktfaktors;
- Abstand zur Bewegung von BTC, ETH oder dem jeweiligen Sektorcluster.

Der **Portfoliozustand** umfasst aktuelle Position, Cash, nicht realisierte
Gewinne/Verluste, Exposure, Drawdown und verbleibendes Risikobudget. Ohne diesen
Block könnte der Agent dieselbe Marktentscheidung treffen, obwohl das Portfolio
bereits völlig unterschiedlich positioniert ist.

### Kein Datensatz enthält automatisch „alle anderen“ korrekt

OHLCV-Daten mehrerer Coins reichen aus, um Indexrendite, Breadth, Korrelation,
relative Stärke und PCA-Faktoren selbst zu berechnen. Marktkapitalisierung,
Dominanz, Funding, Open Interest, Orderbuch und Liquidationen stammen dagegen
häufig aus unterschiedlichen Quellen und haben unterschiedliche Historientiefen.
Darum wird eine versionierte Tabelle pro Zeitpunkt aufgebaut, statt auf einen
vermeintlich vollständigen Gesamtdatensatz zu vertrauen.

Das Universum darf nicht rückwirkend aus den heute größten Coins gebildet werden.
Für jeden Zeitpunkt muss feststehen, welche Coins damals gelistet und liquide
waren. Andernfalls verschwinden gescheiterte oder delistete Coins aus dem Test
und das Ergebnis wird künstlich besser. Bei der Berechnung eines Marktfeatures
für Coin `i` sollte zusätzlich eine `ex_i`-Variante getestet werden, die Coin `i`
aus dem Marktaggregat entfernt. So wird beispielsweise bei einem sehr großen
Coin nicht dessen eigene Bewegung fälschlich als unabhängiges Marktsignal
zurückgespiegelt.

### Diese Information wird per Ablation geprüft

Ob der Gesamtmarktüberblick dem Agenten wirklich hilft, wird nicht vorausgesetzt,
sondern mit vier ansonsten identischen Experimenten gemessen:

| Variante | Agent sieht |
| --- | --- |
| A | nur eigene Coin-Daten |
| B | eigene Daten + BTC/ETH |
| C | eigene Daten + kompakte Marktfeatures |
| D | eigene Daten + Marktfeatures + relative Coin-Merkmale |

Alle Varianten verwenden dieselben Seeds, Walk-forward-Fenster, Kosten und
Risikolimits. Die zusätzlichen Informationen bleiben nur erhalten, wenn sie in
mehreren ungesehenen Fenstern die Nettoergebnisse oder Risikostabilität
verbessern. Dadurch lässt sich beantworten, **welche** Übersicht der Agent benötigt,
anstatt ihm vorsorglich sämtliche verfügbaren Daten zu geben.

## 5. Daten korrekt aufbauen

1. Rohdaten unverändert und mit Quelle, Zeitzone, Downloadzeit und Version
   speichern.
2. Splits, Dividenden, Delistings und Symbolwechsel berücksichtigen.
3. Den tatsächlich handelbaren Preis verwenden: Ein Signal auf Basis des
   Tagesschlusses darf nicht zum selben Schlusskurs ausgeführt werden.
4. Features ausschließlich aus Daten berechnen, die beim Entscheidungszeitpunkt
   bekannt waren. Fundamentaldaten benötigen ihren Veröffentlichungszeitpunkt.
5. Fehlende Werte, Ausreißer, Duplikate und Zeitlücken automatisch prüfen.
6. Bei Aktien ein historisches, punkt-in-Zeit korrektes Universum verwenden, um
   Survivorship Bias zu vermeiden.

Zunächst genügen OHLCV-Daten. Nachrichten, Sentiment oder alternative Daten
sollten erst ergänzt werden, wenn die einfache Pipeline zuverlässig und
leakage-frei läuft.

## 6. Baselines vor komplexen Agenten

Vor Optimierung oder Reinforcement Learning werden einfache Kontrollen gebaut:

- Cash beziehungsweise keine Position;
- Buy-and-Hold;
- gleichgewichtetes Rebalancing;
- Momentum- oder Moving-Average-Regel;
- zufällige Aktionen mit denselben Positionsgrenzen.

Ein komplexer Agent ist nur interessant, wenn er robuste Baselines **nach
identischen Kosten** und auf ungesehenen Daten schlägt.

## 7. Backtest- und Validierungsdesign

### Zeitliche Trennung

Zufällige Train/Test-Splits sind für Zeitreihen ungeeignet. Stattdessen wird
Walk-forward getestet:

```text
Fenster 1: [ Training ][ Validierung ][ Test ]
Fenster 2:       [ Training ][ Validierung ][ Test ]
Fenster 3:             [ Training ][ Validierung ][ Test ]
```

- **Training:** Modellparameter lernen.
- **Validierung:** Hyperparameter und Entscheidungsschwellen wählen.
- **Test:** genau einmal die vorab festgelegte Variante bewerten.
- Zwischen Abschnitten bei überlappenden Labels eine Sperrzone („purging“ und
  „embargo“) einfügen.

Der finale Holdout bleibt bis zum Abschluss der Modellauswahl unangetastet.
Normalisierung, Feature-Auswahl und Regimeklassifikation werden innerhalb jedes
Trainingsfensters neu angepasst.

### Realistische Ausführung

Der Simulator sollte mindestens abbilden:

- Gebühren und Bid-Ask-Spread;
- Slippage in Abhängigkeit von Volatilität und Ordergröße;
- Verzögerung zwischen Signal und Fill;
- Teilfüllungen beziehungsweise ein Volumenlimit pro Kerze;
- Finanzierung, Borrow Fees und fehlende Verfügbarkeit bei Shorts;
- Corporate Actions sowie Margin- und Liquidationsregeln;
- keine Orders bei fehlenden oder ungültigen Marktdaten.

Anschließend werden Kosten und Latenz in Stressszenarien etwa verdoppelt. Eine
Strategie, deren Vorteil dann verschwindet, ist wahrscheinlich zu fragil.

## 8. „Unter welchen Konditionen?“ beantworten

Testperioden werden **nachträglich für die Diagnose**, nicht zur nachträglichen
Regeloptimierung, in Regime zerlegt:

| Dimension | Beispielhafte Definition |
| --- | --- |
| Trend | positiv, seitwärts, negativ anhand langfristiger Rendite |
| Volatilität | Quantile einer rollierenden, annualisierten Volatilität |
| Liquidität | Quantile von Volumen, Spread oder handelbarem Volumen |
| Stress | Drawdown, Volatilitätssprung oder marktweiter Abverkauf |
| Korrelation | niedrige oder hohe mittlere Korrelation im Universum |

Die Grenzen werden ausschließlich auf Trainingsdaten festgelegt. Pro Regime
werden Rendite, Risiko, Turnover, Kosten und Zahl unabhängiger Beobachtungen
berichtet. Kleine Stichproben werden deutlich markiert. So entsteht eine Matrix
„Agent × Marktregime“, aus der hervorgeht, wo ein Agent Mehrwert liefert und wo
er deaktiviert oder begrenzt werden sollte.

## 9. Vergleich von Einzel- und Multi-Agent-Systemen

Alle Varianten erhalten dieselben Daten, Seeds, Zeitfenster, Budgets und
Ausführungsregeln. Sinnvolle Varianten sind:

1. ein einzelner Agent als Kontrollmodell;
2. mehrere identisch trainierte Agenten mit unterschiedlichen Seeds;
3. spezialisierte Agenten, etwa Trend, Mean Reversion und Risiko;
4. ein Ensemble mit festen Gewichten;
5. ein Meta-Agent, der Gewichte oder Aktivierung wählt.

Jede zusätzliche Komponente wird per Ablation entfernt. Nur wenn der Unterschied
über mehrere Walk-forward-Fenster stabil bleibt, ist die zusätzliche Komplexität
gerechtfertigt. Ein Meta-Agent darf Regimeinformationen nur aus der Vergangenheit
verwenden und muss separat validiert werden.

## 10. Kennzahlen und statistische Belastbarkeit

Mindestens zu berichten sind:

- annualisierte Rendite und Volatilität;
- Sharpe und Sortino Ratio;
- maximaler Drawdown und Erholungsdauer;
- Calmar Ratio;
- Turnover, durchschnittliche Haltedauer und Kapazität;
- Brutto- gegenüber Nettorendite sowie Kostenanteil;
- Trefferquote, Profit Factor und Tail-Verluste;
- Exposure und Konzentration nach Instrument und Sektor.

Zusätzlich werden Konfidenzintervalle mit einem zeitabhängigen Block-Bootstrap
geschätzt. Ergebnisse sollten über mehrere Seeds und Zeitfenster dargestellt
werden, nicht nur als bester Lauf. Bei vielen getesteten Varianten müssen
Multiple-Testing- und Selection-Bias berücksichtigt werden. Der vollständige
Versuchsverlauf – einschließlich schlechter Läufe – bleibt erhalten.

## 11. Optimierungsreihenfolge

Die Optimierung erfolgt stufenweise:

1. Daten- und Buchhaltungsfehler beseitigen;
2. Kostenmodell kalibrieren;
3. robuste Baseline etablieren;
4. wenige, begründete Features testen;
5. Hyperparameter nur im Trainings-/Validierungsbereich suchen;
6. Risiko- und Positionsgrößenregeln optimieren;
7. erst dann Ensemble oder Multi-Agent-Logik ergänzen.

Für Hyperparameter eignen sich Random Search oder Bayesian Optimization besser
als eine große erschöpfende Suche. Die Zielfunktion sollte Risiko und Kosten
explizit enthalten, zum Beispiel:

```text
Score = Median(Walk-forward-Sortino)
        - 0,5 * MaxDrawdown
        - 0,2 * Turnover
        - Stabilitätsstrafe
```

Gewichte und Grenzwerte werden vor dem Lauf festgelegt. Niemals wird direkt auf
dem finalen Testset optimiert.

## 12. Automatisierte Tests und Reproduzierbarkeit

Wichtige Tests für die spätere Implementierung:

- Portfolio-Buchhaltung und Gebühren anhand kleiner, von Hand berechneter Fälle;
- kein Zugriff auf zukünftige Zeilen oder spätere Veröffentlichungen;
- deterministische Ergebnisse bei gleichem Seed;
- identische Ergebnisse bei wiederholtem Laden derselben Datenversion;
- Positions-, Hebel- und Liquiditätsgrenzen werden immer eingehalten;
- fehlende Preise erzeugen keine künstlichen Gewinne;
- Baseline-Regressionstests mit bekannten Ergebnissen;
- End-to-End-Smoke-Test eines kurzen Walk-forward-Laufs.

Jeder Lauf speichert Konfiguration, Git-Commit, Daten-Hash, Seed, Bibliotheks-
versionen, Kennzahlen und Artefakte. Ein Experiment ist erst vergleichbar, wenn
es aus diesen Angaben reproduziert werden kann.

## 13. Konkreter erster Meilenstein

Für einen kleinen, belastbaren Start:

1. Einen Markt, eine Frequenz und 5–20 liquide Instrumente auswählen.
2. Eine versionierte OHLCV-Pipeline samt Qualitätsbericht bauen.
3. Buy-and-Hold und eine einfache Momentum-Baseline implementieren.
4. Kosten, Spread, einen Takt Verzögerung und Positionslimits simulieren.
5. Drei oder mehr Walk-forward-Fenster ausführen.
6. Kennzahlen inklusive Bootstrap-Intervallen und Regimetabelle erzeugen.
7. Erst danach den vorhandenen Agenten an dieselbe Schnittstelle anbinden.
8. Paper Trading als letzte Validierungsstufe mehrere Wochen laufen lassen,
   bevor überhaupt über Kapitaleinsatz entschieden wird.

### Bereits gesetzte Forschungsannahmen

Die offenen Varianten sind jetzt maschinenlesbar konfiguriert. Das aggressive
Profil bedeutet in der ersten Forschungsfassung höchstens 20 Prozent Gewicht pro
Coin, 35 Prozent Portfolio-Drawdown-Grenze und bis zu 5x Brutto-Exposure. Das
sind **Testgrenzen und keine Empfehlung für Echtgeld**. Ein Lauf, der die
Drawdown-Grenze berührt, wird gestoppt und als Risikoverletzung berichtet; die
Grenze wird nicht durch nachträgliches Entfernen des schlechten Laufs optimiert.

Als nächster Implementierungsschritt fehlen damit keine Nutzerentscheidungen,
sondern der Datenadapter, die zeitkorrekte Universe-Konstruktion, der Backtester
und der Adapter des Agenten auf die drei Aktionsräume.
