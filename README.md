# MFR Stats-Bot einrichten (kostenlos, ohne eigenen Server)

Der Bot läuft nicht dauerhaft. GitHub Actions startet das Skript alle 10 Minuten,
es setzt die Channelnamen und beendet sich wieder.

## 1. Discord-Bot anlegen (5 Min.)

1. https://discord.com/developers/applications > **New Application** > Name z. B. `MFR Stats`.
2. Links **Bot** > **Reset Token** > Token kopieren und sicher aufbewahren (nie posten, nie in Dateien committen).
3. Auf derselben Seite unter **Privileged Gateway Intents** den **Server Members Intent** einschalten (nur nötig für den Family-Zähler).
4. Links **OAuth2 > URL Generator**: Scope `bot`, Berechtigung **Manage Channels** (Kanäle verwalten).
5. Die erzeugte URL öffnen, den Server `MFR | Gooner No. 1` wählen, bestätigen.
6. In Discord: Bot-Rolle in der Rollenliste **unter Counselor** ziehen. Sie muss keine anderen Rechte haben.

## 2. IDs sammeln

Discord > Einstellungen > Erweitert > **Entwicklermodus** einschalten. Dann per Rechtsklick > **ID kopieren**:

- Server (Rechtsklick auf das Server-Icon) -> `GUILD_ID`
- Die vier Stats-Voice-Channels -> `CH_MEMBERS`, `CH_ONLINE`, `CH_FAMILY`, `CH_DRINKS`
- Rollen Soldier, Capo, Counselor (Servereinstellungen > Rollen > Rechtsklick auf die Rolle) -> `FAMILY_ROLE_IDS`, kommagetrennt. Goon King und Goon Supporter bei Bedarf dazu.

Tipp: Lege für den Drinks-Countdown einen vierten Voice-Channel in der Stats-Kategorie an.

## 3. GitHub einrichten

1. Auf github.com ein neues Repository anlegen, **Public** (siehe Hinweis unten), und diese drei Dinge hochladen:
   `stats_bot.py`, `requirements.txt` und den Ordner `.github/workflows/` mit `stats.yml`.
2. Repo > **Settings > Secrets and variables > Actions**:
   - Reiter **Secrets** > New repository secret: `DISCORD_TOKEN` = dein Bot-Token.
   - Reiter **Variables** > New repository variable, jeweils eine pro Zeile:
     `GUILD_ID`, `CH_MEMBERS`, `CH_ONLINE`, `CH_FAMILY`, `CH_DRINKS`, `FAMILY_ROLE_IDS`, `DRINKS_RESET_LOCAL`.
3. Tab **Actions** > Workflow `Update Stats` > **Run workflow**. Nach etwa 20 Sekunden sollten die Channelnamen stimmen.

`DRINKS_RESET_LOCAL` ist die Reset-Zeit in deutscher Zeit, also `02:00`. Sommer-/Winterzeit wird automatisch beachtet.

## Wichtig zu wissen

- **Public Repo:** Private Repos haben nur 2000 Gratis-Minuten pro Monat, alle 10 Minuten reichen dafür nicht. Im Public Repo ist das unbegrenzt. Der Token steht als Secret und ist nicht sichtbar. Schreib ihn aber nie in eine Datei.
- **Zeitraster:** GitHub startet geplante Läufe oft einige Minuten später. Der Countdown ist daher ungenau. Discord begrenzt Channel-Umbenennungen ohnehin auf etwa 2 pro 10 Minuten.
- **Inaktivität:** GitHub deaktiviert geplante Workflows nach 60 Tagen ohne Repo-Aktivität. Dann im Actions-Tab wieder aktivieren oder einen Commit machen.
- **Token geleakt?** Sofort im Developer Portal `Reset Token` und das Secret in GitHub ersetzen.
- Der Family-Zähler zählt Mitglieder mit mindestens einer der angegebenen Rollen, Bots ausgenommen.

## Alternative: Dauerbetrieb

Wenn dir 10-Minuten-Takt reicht, bleib bei GitHub Actions. Für einen echten Dauerlauf starte das Skript mit
`python stats_bot.py --loop` auf einem Raspberry Pi oder einem Gratis-Hoster. Die Umgebungsvariablen sind
dieselben wie oben.
