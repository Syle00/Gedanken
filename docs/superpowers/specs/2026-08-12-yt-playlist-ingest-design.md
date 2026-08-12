# yt-playlist-ingest — Design

## Zweck

Große YouTube-Playlisten (50-500+ Videos, beliebige Domäne, nicht nur Trading) zuverlässig und
IP-Ban-sicher importieren: Rohtranskripte nach `raw/<domäne>/`, danach normaler
CLAUDE.md-Ingest-Workflow zu `wiki/`. Verteilt sich bei Bedarf über mehrere Sessions/Tage, ohne
bei einem Abbruch von vorn anfangen zu müssen.

## Kontext

Der bestehende Skill `yt-ict-ingest` (`.claude/skills/yt-ict-ingest/SKILL.md`) importiert einzelne
neue Videos vom Kanal `@InnerCircleTrader`, gefiltert nach Trading-Relevanz. Er nutzt
`tools/fetch_yt_transcript.py` (holt Metadaten via `yt-dlp`, Transkript via
`youtube_transcript_api`, ein Video pro Aufruf) und hat empirisch bestätigte Pacing-Regeln
gegen `IpBlocked`: strikt seriell, 45s Pause zwischen Videos, 90s zum Ende eines langen Batches;
ein 9-Video-Batch in einer Session lief 2026-08-10 ohne Block. Der historische `IpBlocked`-Auslöser
war immer paralleler Zugriff (Subagenten), nicht Volumen allein.

Dieser Skill verallgemeinert das Muster für **beliebige Playlisten in beliebigen Domänen** und
fügt hinzu, was für große Playlisten zusätzlich nötig ist: Enumeration einer ganzen Playlist
(nicht nur Einzelvideos), Fortsetzbarkeit über Sessions hinweg, und einen domänen-neutralen
Wiki-Ingest-Schritt (kein ICT-spezifischer Inhaltsfilter).

## Architekturentscheidung

Neues, separates Skript `tools/fetch_yt_playlist.py`, das `get_metadata()` und
`get_transcript_text()` aus `tools/fetch_yt_transcript.py` importiert, statt dieses Skript zu
ändern. Grund: `yt-ict-ingest` hängt an `fetch_yt_transcript.py` — jede Änderung daran trägt das
Risiko, den bestehenden, funktionierenden Kanal-Ingest-Workflow zu destabilisieren. Ein separates
Skript hält den Diff klein und den bestehenden Workflow unangetastet.

## Komponenten

### 1. `tools/fetch_yt_playlist.py` (neu)

**Enumeration:**
```
python -m yt_dlp --flat-playlist --print "%(id)s | %(title)s" "<playlist-url>"
```

**Checkpoint-Datei:** `raw/<domäne>/.yt_playlist_state/<playlist_id>.json`

```json
{
  "playlist_id": "PL...",
  "playlist_title": "...",
  "videos": [
    {"id": "abc123", "title": "...", "status": "done"},
    {"id": "def456", "title": "...", "status": "pending"},
    {"id": "ghi789", "title": "...", "status": "skipped_no_captions"}
  ]
}
```

- `status` ∈ `pending | done | skipped_no_captions | failed`
- Gitignored (transientes Betriebsstate, analog `algo/live/<datum>/` — siehe
  Versionskontrolle-Abschnitt in `CLAUDE.md`). Ergänze `.yt_playlist_state/` in `.gitignore`.

**Domänen-Vorschlag:** Beim ersten Lauf für eine neue Playlist-ID leitet das Skript aus
Playlist-Titel (Fallback: Kanalname) eine Domäne ab (z.B. "Clean Code Playlist" →
`coding`) und meldet den Vorschlag im Output. Folgt der bestehenden CLAUDE.md-Regel, neue
`raw/<domäne>/`-Ordner ohne Rückfrage anzulegen. Der Nutzer sieht die gewählte Domäne im
Bericht und kann sie im nächsten Lauf per `--out-dir` übersteuern, falls die Ableitung daneben
liegt (kein Blocker, nur eine Berichtszeile).

**Dedup:** Vor dem Fetch prüft das Skript sowohl den Checkpoint als auch existierende
`raw/<domäne>/**/yt-<id>-transcript.md`-Dateien — bereits vorhandene IDs werden übersprungen,
auch wenn kein Checkpoint-Eintrag existiert (z.B. weil ein Video schon einzeln über
`yt-ict-ingest` geholt wurde).

**Ablauf pro Video (seriell):**
1. Status im Checkpoint auf `pending` (falls neu).
2. `get_metadata(video_id)` + `get_transcript_text(video_id)` aufrufen (importiert aus
   `fetch_yt_transcript.py`), Datei nach `raw/<domäne>/yt-<id>-transcript.md` schreiben (gleiches
   Format wie der bestehende Single-Video-Fetch).
3. Bei Erfolg: Checkpoint-Status `done`.
4. Bei "Subtitles are disabled": Checkpoint-Status `skipped_no_captions`, weiterlaufen (kein
   Whisper-Fallback, kein Abbruch — keine ffmpeg-Abhängigkeit für diesen Skill).
5. Bei `youtube_transcript_api._errors.IpBlocked`: Checkpoint-Status des aktuellen Videos bleibt
   `pending` (nicht `failed` — es wurde nichts Falsches versucht, nur blockiert), Skript beendet
   sich sofort mit Exit-Code ≠ 0 und einer Meldung "X von Y geholt, gestoppt bei Video Z wegen
   IP-Block, Rest folgt beim nächsten Lauf".
6. Pause 45s vor dem nächsten Video; 90s statt 45s, sobald in der laufenden Session bereits 10
   Videos seriell geholt wurden (gleiche Schwelle wie im ICT-Skill dokumentiert).

**Resume:** Erneuter Aufruf mit derselben Playlist-URL liest den vorhandenen Checkpoint, überspringt
`done`- und `skipped_no_captions`-Einträge, macht bei den verbleibenden `pending`-Einträgen weiter.
Kein separater "ab hier weiter"-Parameter nötig.

**CLI:**
```
python tools/fetch_yt_playlist.py <playlist-url> [--out-dir raw/<domäne>]
```
`--out-dir` optional; ohne Angabe nutzt das Skript die automatische Domänen-Ableitung.

### 2. `.claude/skills/yt-playlist-ingest/SKILL.md` (neu)

Struktur analog `yt-ict-ingest/SKILL.md`:

1. **Fetch-Schritt:** `fetch_yt_playlist.py` mit der vom Nutzer gegebenen Playlist-URL aufrufen,
   Bericht (geholt/übersprungen/gestoppt) lesen.
2. **Wiki-Ingest-Schritt:** Für jedes neu geholte Transkript den **allgemeinen Ingest-Workflow aus
   `CLAUDE.md`** anwenden — `wiki/sources/youtube/<datum> - <Titel> (Source).md`,
   Concept-/Model-Seiten bei inhaltlichem Bedarf, `wiki/index.md` aktualisieren. **Kein**
   domänenspezifischer Inhaltsfilter wie bei ICT ("meine Regeln") — das ist bewusst allgemein
   gehalten, weil der Skill domänenunabhängig sein soll.
3. **Batch-Wrapup:** Ein `wiki/log.md`-Eintrag (Typ `ingest`) pro Session-Batch: Playlist-Titel,
   wie viele geholt/übersprungen/gestoppt, Domäne. Ein `.\push.ps1`-Aufruf am Ende der Session
   (nicht mitten im laufenden Fetch — ein mehrtägiger Import bedeutet mehrere Push-Aufrufe, einen
   pro Session-Batch, nicht einen für die gesamte Playlist).
4. **Gotchas-Abschnitt:** Gleiche IP-Ban-Hinweise wie in `yt-ict-ingest` (strikt seriell, keine
   parallelen Subagenten, `--`-Separator für Video-/Playlist-IDs die mit `-` beginnen,
   `--flat-playlist` liefert kein Upload-Datum).

### 3. Selbstcheck

`tools/fetch_yt_playlist.py` bekommt einen `demo()`/`if __name__ == "__main__" and "--selftest"`-Block
(oder eine kleine `test_fetch_yt_playlist.py`, je nachdem was schlanker ist), der Checkpoint-Lesen/
-Schreiben und die Resume-Logik gegen eine Fake-Playlist mit 3 Einträgen (einer davon `done`)
prüft — ohne echten Netzwerk-Call. Erwartung: nur die 2 verbleibenden `pending`-Einträge werden
als "zu holen" markiert.

## Fehlerbehandlung — Zusammenfassung

| Fall | Verhalten |
|---|---|
| Captions deaktiviert | Video als `skipped_no_captions` markieren, weiterlaufen, im Bericht/Log nennen |
| `IpBlocked` | Sofort stoppen, Checkpoint bleibt konsistent (aktuelles Video bleibt `pending`), Exit-Code ≠ 0, klare Meldung |
| Video-ID beginnt mit `-` | `--`-Separator verwenden (wie im ICT-Skill dokumentiert) |
| Playlist bereits (teilweise) geholt | Dedup gegen Checkpoint + vorhandene `raw/`-Dateien, kein erneutes Fetchen |

## Out of Scope

- Kein Whisper-/ffmpeg-Fallback für Videos ohne Auto-Captions.
- Keine automatische Fortsetzung via `schedule`-Skill bei einem `IpBlocked`-Abbruch — der Nutzer
  ruft den Skill bei Bedarf manuell erneut auf (Checkpoint macht das trivial).
- Kein domänenspezifischer Inhaltsfilter (das bleibt Aufgabe von domänenspezifischen Skills wie
  `yt-ict-ingest`, falls für eine bestimmte Playlist gewünscht).
- Kein Proxy-/IP-Rotationsmechanismus — die bereits bestätigte serielle Pacing-Strategie reicht
  laut bisheriger Erfahrung aus; das wäre Overengineering ohne belegten Bedarf.
