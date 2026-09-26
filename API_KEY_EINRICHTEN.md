# API-Key einrichten

## Wichtig: Nicht in `.env.example` eintragen

`.env.example` ist nur eine öffentliche Vorlage. Dort darf kein echter API-Key
stehen, weil diese Datei in Git eingecheckt wird.

Der echte Key gehört in eine separate Datei namens `.env`, die von Git ignoriert
wird.

## Mit bearbeitbarer Dateiansicht

1. `.env.example` kopieren.
2. Die Kopie exakt `.env` nennen.
3. In der neuen `.env` diese Zeile ausfüllen:

   ```dotenv
   MODEL_API_KEY=hier_den_echten_key_einfügen
   ```

4. `.env` speichern. `.env.example` unverändert lassen.

## Direkt auf GitHub.com

Ein Repository zeigt Secrets nicht in der normalen Dateiansicht. Dafür sind auf
GitHub Repository-Administrationsrechte erforderlich:

1. Das Repository auf GitHub öffnen.
2. Oben im Repository **Settings** wählen. Fehlt der Reiter, fehlen die nötigen
   Repository-Rechte.
3. Links **Secrets and variables** aufklappen.
4. **Actions** wählen.
5. **New repository secret** wählen.
6. Genau diesen Eintrag anlegen:

| Feld | Inhalt |
| --- | --- |
| Name | `MODEL_API_KEY` |
| Value/Wert | der persönliche API-Key |

7. **Add secret** wählen.
8. Unter **Actions** den Workflow **Check model API key** manuell starten. Der
   Workflow reicht das Secret als Umgebungsvariable an den Prüfer weiter, ohne
   den Wert auszugeben.

Der technische Name muss exakt `MODEL_API_KEY` lauten: Großbuchstaben und
Unterstriche, keine Leerzeichen. Die Schreibweise „Model API Key“ als sichtbare
Beschreibung reicht nicht, wenn das Feld tatsächlich Leerzeichen speichert.

Ein Secret, das während eines bereits laufenden Jobs oder einer bereits offenen
Agentensitzung angelegt wird, erscheint dort nicht nachträglich. Nach dem
Speichern muss ein **neuer** Workflow-Lauf beziehungsweise eine **neue** Sitzung
gestartet werden.

Eine weitere Nachricht im selben Chat ist **keine neue Sitzung**. Wenn das
Secret in der Umgebung dieser Agentenoberfläche angelegt wurde, muss dieser Task
beendet und ein vollständig neuer Task aus derselben aktualisierten Umgebung
gestartet werden. Der aktuelle Prozess kann seine beim Start erhaltenen
Umgebungsvariablen nicht nachladen.

Ein GitHub-Actions-Secret wird nicht automatisch in eine lokale `.env` kopiert.
Es ist ausschließlich für GitHub-Actions-Läufe verfügbar. Der Key wird nicht in
den Chat, einen Kommentar oder eine Diff-Ansicht kopiert.

### Repository-Secret oder Environment-Secret

Die mitgelieferte Prüfung erwartet ein **Repository secret** unter
`Settings → Secrets and variables → Actions → Repository secrets`. Ein Secret,
das stattdessen innerhalb eines benannten GitHub-**Environments** angelegt wurde,
ist nur für Jobs verfügbar, die genau diesem Environment zugeordnet sind. Ohne
diese Zuordnung bleibt es für den Workflow unsichtbar. Für die aktuelle Prüfung
deshalb `MODEL_API_KEY` unter **Repository secrets** anlegen.

### Wo „Run workflow“ zu finden ist

Der Knopf ist erst sichtbar, wenn die Workflow-Datei im **Standard-Branch** des
Repositories liegt. Solange diese Änderung nur in einem offenen Pull Request
steht, kann der Workflow auf GitHub noch nicht manuell gestartet werden.

1. Diesen Pull Request zuerst in den Standard-Branch mergen.
2. Danach die Hauptseite des GitHub-Repositories neu laden.
3. In der oberen Repository-Navigation **Actions** öffnen – nicht „Settings“.
4. In der linken Spalte unter **All workflows** auf
   **Check model API key** klicken.
5. Auf der Workflow-Seite befindet sich oberhalb der Liste bisheriger Läufe
   rechts ein Knopf beziehungsweise Dropdown **Run workflow**.
6. **Run workflow** öffnen, den Standard-Branch ausgewählt lassen und im
   Dropdown erneut den grünen Knopf **Run workflow** drücken.

Fehlt der Knopf danach weiterhin, ist mindestens eine dieser Voraussetzungen
nicht erfüllt: Der Workflow ist noch nicht im Standard-Branch, GitHub Actions
ist für das Repository deaktiviert oder das angemeldete Konto besitzt keine
Schreibberechtigung. Eine noch nicht gemergte Diff-/PR-Ansicht zeigt diesen
Knopf nicht.

Erst der so gestartete neue GitHub-Lauf erhält das Repository-Secret.

## Prüfen

Mit einem Terminal kann die lokale Datei geladen und geprüft werden:

```bash
cd /workspace/game
set -a
source .env
set +a
PYTHONPATH=src python -m tradinglab.secrets
```

Der Prüfer gibt den Key nicht aus. Erwartet wird `"model_ready": true`.

`BYBIT_API_KEY` und `BYBIT_API_SECRET` bleiben für öffentliche historische Daten
leer.
