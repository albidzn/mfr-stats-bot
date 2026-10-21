"""
Kleiner Stats-Bot: aktualisiert die Namen von Voice-Channels mit Live-Zahlen.
Nutzt nur die Discord-REST-API, kein Dauerbetrieb nötig.

Pflicht-Variablen:
  DISCORD_TOKEN   Bot-Token
  GUILD_ID        Server-ID
Channel-IDs (leer lassen = Zähler wird übersprungen):
  CH_MEMBERS, CH_ONLINE, CH_FAMILY, CH_DRINKS
Optional:
  FAMILY_ROLE_IDS   Rollen-IDs, kommagetrennt (Soldier, Capo, Counselor, ...)
  DRINKS_RESET_LOCAL  Reset-Uhrzeit in lokaler Zeit, z. B. 02:00
  DRINKS_TZ         Zeitzone (Standard Europe/Berlin)
  NAME_MEMBERS / NAME_ONLINE / NAME_FAMILY / NAME_DRINKS  Namensvorlagen
  INTERVAL          Sekunden zwischen Updates im --loop-Modus (Standard 600)
"""
import os
import sys
import time
import datetime as dt
from zoneinfo import ZoneInfo

import requests

API = "https://discord.com/api/v10"
TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = os.environ["GUILD_ID"]
HEADERS = {
    "Authorization": f"Bot {TOKEN}",
    "User-Agent": "MFR-StatsBot (custom, 1.0)",
}


def env(name, default=""):
    return os.environ.get(name, default).strip()


def call(method, path, **kwargs):
    for _ in range(4):
        r = requests.request(method, API + path, headers=HEADERS, timeout=20, **kwargs)
        if r.status_code == 429:
            time.sleep(float(r.json().get("retry_after", 5)) + 0.5)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Rate limit bei {method} {path}")


def guild_counts():
    g = call("GET", f"/guilds/{GUILD_ID}", params={"with_counts": "true"})
    return g["approximate_member_count"], g["approximate_presence_count"]


def family_count(role_ids):
    """Zählt Nicht-Bots mit mindestens einer der Rollen.
    Braucht 'Server Members Intent' im Developer Portal."""
    total, after = 0, "0"
    while True:
        page = call("GET", f"/guilds/{GUILD_ID}/members",
                    params={"limit": 1000, "after": after})
        for m in page:
            if m["user"].get("bot"):
                continue
            if role_ids & set(m["roles"]):
                total += 1
        if len(page) < 1000:
            return total
        after = page[-1]["user"]["id"]


def drinks_text(reset_local):
    """Reset-Zeit in deutscher Zeit (Sommer-/Winterzeit wird automatisch beachtet)."""
    tz = ZoneInfo(env("DRINKS_TZ", "Europe/Berlin"))
    hh, mm = (int(x) for x in reset_local.split(":"))
    now = dt.datetime.now(tz)
    nxt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if nxt <= now:
        nxt += dt.timedelta(days=1)
    mins = int((nxt - now).total_seconds() // 60)
    return f"{mins // 60}h {mins % 60:02d}m"


def set_name(channel_id, name):
    if not channel_id:
        return
    current = call("GET", f"/channels/{channel_id}")["name"]
    if current == name:
        print(f"unverändert: {name}")
        return
    call("PATCH", f"/channels/{channel_id}", json={"name": name})
    print(f"gesetzt: {name}")


def run_once():
    members, online = guild_counts()
    set_name(env("CH_MEMBERS"),
             env("NAME_MEMBERS", "👥 Members: {n}").format(n=members))
    set_name(env("CH_ONLINE"),
             env("NAME_ONLINE", "🟢 Online: {n}").format(n=online))

    roles = {r.strip() for r in env("FAMILY_ROLE_IDS").split(",") if r.strip()}
    if env("CH_FAMILY") and roles:
        set_name(env("CH_FAMILY"),
                 env("NAME_FAMILY", "🎩 Family: {n}").format(n=family_count(roles)))

    if env("CH_DRINKS") and env("DRINKS_RESET_LOCAL"):
        set_name(env("CH_DRINKS"),
                 env("NAME_DRINKS", "🍸 Drinks reset in: {t}")
                 .format(t=drinks_text(env("DRINKS_RESET_LOCAL"))))


if __name__ == "__main__":
    if "--loop" in sys.argv:
        interval = int(env("INTERVAL", "600"))
        while True:
            try:
                run_once()
            except Exception as exc:  # Bot soll nicht wegen eines Fehlers sterben
                print("Fehler:", exc)
            time.sleep(interval)
    else:
        run_once()
