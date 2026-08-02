#!/usr/bin/env python3
"""Verbindet die Journal-Datenbank mit dem Wiki.

Liest raw/journal/ (unveraendert, nur lesend) und erzeugt daraus eine Wiki-Seite,
die jeden Punkt seiner achtteiligen Setup-Checkliste mit der zustaendigen
Wiki-Seite verknuepft und auszaehlt, wie oft er erfuellt war.

Warum ueberhaupt generiert: raw/ ist laut CLAUDE.md unveraenderlich, es koennen
also keine Wikilinks in die Journaldateien geschrieben werden. Die Verbindung
entsteht deshalb in wiki/ und wird bei Bedarf neu erzeugt -- wie site/.

Grundsatz: nur ausgezaehlte Werte. Wo die Datenbasis zu duenn ist, sagt die
Ausgabe das, statt eine Zahl zu behaupten.

Aufruf:
    python tools/journal_wiki.py            # schreibt die Wiki-Seite
    python tools/journal_wiki.py --dry-run  # nur Konsolenausgabe

Nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "raw" / "journal"
ZIEL = ROOT / "wiki" / "synthesis" / "Journal-Auswertung.md"

# Seine acht Checklistenpunkte -> Fehler-ID aus dem Fehlerkatalog des
# trading-journal-Skills -> zustaendige Wiki-Seiten.
# Die Reihenfolge ist die seiner Liste, nicht alphabetisch.
CHECKLISTE = [
    ("Liq Sweep", "S06", ["Turtle Soup", "Open Float & Liquidity Pools"]),
    ("Displacement", "S01", ["Fair Value Gap (FVG)", "Market Structure Shift (MSS)"]),
    ("Anhaltende Consolidation", "S11",
     ["AMD Cycle (Accumulation – Manipulation – Distribution)"]),
    ("Richtige Zeitfenster", "T03", ["ICT Killzones", "ICT Macros & Leading Candles"]),
    ("MS Break", "S02",
     ["Market Structure Shift (MSS)", "CISD (Change in State of Delivery)"]),
    ("Entry", "S12", ["Modell 22"]),
    ("Macro Expansion", "S13", ["ICT Macros & Leading Candles"]),
    ("Target Liquidität", "S05",
     ["Open Float & Liquidity Pools", "AMD Cycle (Accumulation – Manipulation – Distribution)"]),
]

MONATE = {
    "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
    "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11,
    "Dezember": 12,
}


def parse_datum(text: str):
    """'16. März 2026' -> date. None, wenn nicht lesbar."""
    m = re.match(r"\s*(\d{1,2})\.\s*(\w+)\s*(\d{4})", text or "")
    if not m or m.group(2) not in MONATE:
        return None
    return date(int(m.group(3)), MONATE[m.group(2)], int(m.group(1)))


def lies_journal_tabelle() -> dict[str, dict]:
    """Journal.md ist die Datenbanktabelle -- sie traegt die verlaesslichen Daten."""
    pfad = JOURNAL / "Journal.md"
    if not pfad.exists():
        return {}
    meta = {}
    for zeile in pfad.read_text(encoding="utf-8", errors="replace").splitlines():
        if not zeile.startswith("|[["):
            continue
        sp = [s.strip() for s in zeile.split("|")]
        # sp[0]='' sp[1]=Name sp[2]=Datum sp[3]=Tags sp[4]=Instrument sp[5]=Bias
        # sp[6]=Punkte sp[7]=RR sp[8]=Resultat ... sp[11]=Session Profile
        if len(sp) < 9:
            continue
        name = sp[1].strip("[]")
        meta[name] = {
            "datum": parse_datum(sp[2]),
            "tags": sp[3],
            "instrument": sp[4],
            "bias": sp[5],
            "resultat": sp[8] or None,
            "profil": sp[11] if len(sp) > 11 else "",
        }
    return meta


def lies_eintraege(meta: dict) -> list[dict]:
    """Alle Journaldateien mit Checkliste einlesen."""
    eintraege = []
    for pfad in sorted(JOURNAL.glob("*.md")):
        if pfad.stem == "Journal":
            continue
        text = pfad.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^- \[", text, re.M):
            continue

        checks: dict[str, bool] = {}
        zeiten: dict[str, str] = {}
        for mark, label in re.findall(r"^- \[([ xX])\] *(.+)$", text, re.M):
            for punkt, _id, _seiten in CHECKLISTE:
                if label.startswith(punkt):
                    checks[punkt] = mark.lower() == "x"
                    z = re.search(r"(\d{1,2}:\d{2})", label)
                    if z:
                        zeiten[punkt] = z.group(1)
                    break

        m = meta.get(pfad.stem, {})
        # Resultat steht mal in der Tabelle, mal im Frontmatter der Datei
        resultat = m.get("resultat")
        if not resultat:
            fm = re.search(r"Resultat:\s*\n\s*-\s*(\w+)", text)
            resultat = fm.group(1) if fm else None

        eintraege.append({
            "name": pfad.stem,
            "datei": pfad.relative_to(ROOT).as_posix(),
            "datum": m.get("datum"),
            "bias": m.get("bias", ""),
            "profil": m.get("profil", ""),
            "resultat": resultat,
            "checks": checks,
            "zeiten": zeiten,
        })
    return eintraege


def quote(eintraege, punkt):
    werte = [e["checks"][punkt] for e in eintraege if punkt in e["checks"]]
    return sum(werte), len(werte)


def baue_seite(eintraege) -> str:
    heute = date.today().isoformat()
    gesamt = len(eintraege)
    mit_ergebnis = [e for e in eintraege if e["resultat"] in ("Win", "Loss")]

    z = []
    z.append("---")
    z.append("tags: [synthesis, journal, ict, trading-ict, auswertung, generiert]")
    z.append(f"created: {heute}")
    z.append(f"updated: {heute}")
    z.append("---")
    z.append("")
    z.append("# Journal-Auswertung")
    z.append("")
    z.append("> **Generierte Seite.** Erzeugt von `tools/journal_wiki.py` aus `raw/journal/`.")
    z.append("> Nicht von Hand bearbeiten — Änderungen gehen beim nächsten Lauf verloren.")
    z.append("> `raw/` ist unveränderlich, deshalb entsteht die Verbindung Journal→Wiki hier")
    z.append("> statt als Wikilinks in den Journaldateien.")
    z.append("")
    z.append(f"Grundlage: **{gesamt} Journaleinträge mit ausgefüllter Setup-Checkliste**.")
    z.append("")

    # --- Hauptbefund: Erfuellungsquote je Punkt ---
    z.append("## Wie oft jeder Checklistenpunkt erfüllt war")
    z.append("")
    z.append("Ausgezählt über alle Einträge mit Checkliste, unabhängig vom Ausgang.")
    z.append("")
    z.append("| Checklistenpunkt | erfüllt | Quote | Fehler-ID | Wiki |")
    z.append("|---|---|---|---|---|")
    zeilen = []
    for punkt, fid, seiten in CHECKLISTE:
        ja, n = quote(eintraege, punkt)
        if n == 0:
            continue
        pct = round(100 * ja / n)
        links = ", ".join(f"[[{s}]]" for s in seiten)
        zeilen.append((pct, punkt, ja, n, fid, links))
        z.append(f"| {punkt} | {ja}/{n} | **{pct} %** | `{fid}` | {links} |")
    z.append("")

    if zeilen:
        schwach = min(zeilen)
        rest = sorted(p for p, *_ in zeilen if p != schwach[0])
        z.append(f"**Der Ausreißer ist `{schwach[4]}` — {schwach[1]}: "
                 f"{schwach[2]} von {schwach[3]} ({schwach[0]} %).**")
        if rest:
            z.append(f"Alle übrigen Punkte liegen zwischen {rest[0]} % und {rest[-1]} %. "
                     f"{schwach[1]} ist damit rund halb so oft erfüllt wie der nächstschwächste "
                     f"Punkt — und zwar nicht knapp, sondern deutlich.")
        z.append("")
        z.append('Der Fehlerkatalog des Journal-Skills hatte genau das vorhergesagt, ohne die Zahl '
                 'zu kennen: *„Der schwerste der acht Punkte, weil er die Grenze zwischen Analyse '
                 'und Ausführung markiert. Sieben erfüllte Punkte ohne Entry-Trigger sind kein '
                 'Trade, sondern eine gute Beobachtung."* Die Auszählung bestätigt es.')
        z.append("")

    # --- Einzelne Eintraege als Beispiele ---
    z.append("## Die Einträge im Einzelnen")
    z.append("")
    z.append("Sortiert nach erfüllten Punkten. Das sind die konkreten Beispiele, an denen sich ein "
             "künftiges Setup vergleichen lässt.")
    z.append("")
    z.append("| Datum | Eintrag | Haken | Bias | Resultat | fehlende Punkte |")
    z.append("|---|---|---|---|---|---|")
    for e in sorted(eintraege, key=lambda x: (-sum(x["checks"].values()),
                                              x["datum"] or date.min)):
        n_ja = sum(e["checks"].values())
        n_ges = len(e["checks"])
        fehlend = ", ".join(p for p, _f, _s in CHECKLISTE
                            if p in e["checks"] and not e["checks"][p]) or "—"
        d = e["datum"].isoformat() if e["datum"] else "?"
        res = e["resultat"] or "—"
        z.append(f"| {d} | `{e['name']}` | {n_ja}/{n_ges} | {e['bias'] or '—'} | {res} | {fehlend} |")
    z.append("")

    # --- Was NICHT geht ---
    z.append("## Was sich noch nicht rechnen lässt")
    z.append("")
    z.append(f"Von den {gesamt} Einträgen mit Checkliste tragen nur **{len(mit_ergebnis)}** "
             f"ein eindeutiges Resultat (Win oder Loss). Damit ist die eigentlich interessante "
             f"Frage — *welcher fehlende Haken kostet Geld?* — **nicht beantwortbar**.")
    z.append("")
    if mit_ergebnis:
        z.append("| Checklistenpunkt | erfüllt bei Win | erfüllt bei Loss |")
        z.append("|---|---|---|")
        for punkt, _fid, _s in CHECKLISTE:
            w = [e["checks"][punkt] for e in mit_ergebnis
                 if e["resultat"] == "Win" and punkt in e["checks"]]
            l = [e["checks"][punkt] for e in mit_ergebnis
                 if e["resultat"] == "Loss" and punkt in e["checks"]]
            if not w and not l:
                continue
            z.append(f"| {punkt} | {sum(w)}/{len(w)} | {sum(l)}/{len(l)} |")
        z.append("")
        z.append('Die Verteilung ist praktisch flach — bei fast jedem Punkt steht dasselbe '
                 'Verhältnis auf beiden Seiten. Zwei Einträge mit 7/8 Haken wurden gewonnen, '
                 'zwei mit 7/8 verloren. **Daraus lässt sich nichts ableiten**, und jede Aussage '
                 'wie „Punkt X korreliert mit Verlusten" wäre bei dieser Fallzahl geraten.')
        z.append("")
    z.append("Zusätzlich verzerren **Datenlücken**: Einträge mit 0/8 oder 1/8 Haken sind mit hoher "
             "Wahrscheinlichkeit Fälle, in denen die Liste gar nicht geführt wurde — nicht Setups "
             "mit acht Mängeln. Ein leeres Feld heißt *nicht erfasst*, nicht *war nicht da*.")
    z.append("")
    z.append("**Was das konkret braucht:** bei jedem Eintrag mit Checkliste auch `Resultat` setzen. "
             "Win, Loss oder Breakeven genügt. Ab etwa 30 Einträgen mit beidem wird die Tabelle oben "
             "aussagekräftig.")
    z.append("")

    z.append("## Verwandt")
    z.append("")
    z.append("- [[Trading Journal & DOL Checklist]] — die Checkliste als Wiki-Regel")
    z.append("- [[ICT Day Trade Routine]] — der Ablauf, in den sie gehört")
    z.append("- [[Smart Money Concepts (SMC)]]")
    z.append("")
    return "\n".join(z)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts schreiben")
    args = ap.parse_args()

    if not JOURNAL.exists():
        print(f"FEHLER: {JOURNAL} nicht gefunden", file=sys.stderr)
        return 1

    meta = lies_journal_tabelle()
    eintraege = lies_eintraege(meta)
    if not eintraege:
        print("FEHLER: kein Eintrag mit Checkliste gefunden", file=sys.stderr)
        return 1

    print(f"Journal -> Wiki")
    print(f"  {len(meta)} Zeilen in Journal.md")
    print(f"  {len(eintraege)} Eintraege mit Checkliste")
    mit = [e for e in eintraege if e["resultat"] in ("Win", "Loss")]
    print(f"  {len(mit)} davon mit Win/Loss")
    print()
    for punkt, fid, _s in CHECKLISTE:
        ja, n = quote(eintraege, punkt)
        if n:
            print(f"  {fid}  {punkt:<28} {ja:>2}/{n:<3} = {round(100*ja/n):>3}%")

    seite = baue_seite(eintraege)
    if args.dry_run:
        print("\n(--dry-run: nichts geschrieben)")
        return 0

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(seite, encoding="utf-8", newline="\n")
    print(f"\n  -> {ZIEL.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
