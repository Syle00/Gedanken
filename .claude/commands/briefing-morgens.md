---
description: Cowork-Morgenbriefing -- geplant in Claude Desktop, laeuft lokal in diesem Ordner
schedule: "0 7 * * *"
expect: "algo/live/briefing-{today}-morgens.md"
timeout: 60m
extern: true
---

Dieser Eintrag wird vom Taktgeber **nur beobachtet, nie gestartet** (`extern: true`).

Geplant ist er in Claude Desktop unter "Chat und Cowork" -> "Geplant" -> "Daily briefing",
Ordner `C:\Users\janne\OneDrive\Desktop\Ablage 1\VS Folder 1`. Coworks Planer ist von
aussen nicht ansteuerbar; `tools/agent_tick.py` prueft daher nur, ob das Briefing seine
Datei geschrieben hat, und meldet einen Ausfall.

Damit das funktioniert, muss die Cowork-Anweisung diese beiden Saetze enthalten:

1. "Schreibe das fertige Briefing zusaetzlich nach
   `algo/live/briefing-<YYYY-MM-DD>-morgens.md`."
2. "Lies zu Beginn `algo/live/agent-status.md` und uebernimm offene Punkte daraus in
   einen Abschnitt 'Vault & Algo'."

Das `timeout: 60m` ist hier ein Kulanzfenster: erst eine Stunde nach der geplanten Zeit
gilt das Briefing als ausgeblieben.
