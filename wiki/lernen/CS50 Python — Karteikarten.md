---
tags: [flashcards, lernen, cs50]
created: 2026-08-26
updated: 2026-08-26
---

# CS50 Python — Karteikarten

Fertige Karten für das Plugin *Spaced Repetition* (Einrichtung siehe
[[CS50 — Karteikarten & Handy-Sync einrichten]]). Jede Zeile mit `::` ist eine Karte.
Neue Karten einfach unten anhängen.

Stapel: `#flashcards/cs50/python`

---

## Datentypen

Was liefert `input()` immer zurück?::Einen **String** — nie eine Zahl, auch wenn du eine Ziffer eintippst.

Was ergibt `input("Zahl: ")` + sich selbst, wenn du 5 eintippst?::`"55"` — zwei Strings werden aneinandergehängt, nicht addiert.

Wie machst du aus einer Eingabe eine Ganzzahl?::`x = int(input("Zahl: "))`

Was ist der Unterschied zwischen `5` und `"5"`?::`5` ist ein int (Zahl, rechenbar), `"5"` ist ein str (Text, wird nur aneinandergehängt).

Wofür steht `float`?::Für eine Kommazahl, z. B. `2.0` oder `3.5`. Python schreibt den **Punkt**, nicht das Komma.

Wie fragst du ab, welchen Typ ein Wert hat?::`type(x)` — z. B. `type("5")` → `<class 'str'>`

---

## Rechnen

Was ergibt `int(3.9)`?::`3` — `int()` **schneidet ab**, es rundet nicht.

Was ergibt `int(-3.9)`?::`-3` — abgeschnitten Richtung Null, nicht Richtung −4.

Wie rundest du richtig?::Mit `round()`. `round(3.9)` → `4`

Was ergibt `6 / 3`?::`2.0` — `/` liefert **immer** einen float, auch wenn es aufgeht.

Was ergibt `7 // 2`?::`3` — `//` ist die Ganzzahldivision (Ergebnis ohne Rest).

Was ergibt `7 % 2`?::`1` — `%` liefert den **Rest** der Division.

Wie testest du, ob eine Zahl gerade ist?::`if x % 2 == 0:` — Rest 0 bei Division durch 2.

Wie rundest du auf 2 Nachkommastellen bei der Ausgabe?::Mit f-String: `print(f"{x:.2f}")`

---

## Ausgabe

Wie baust du einen Text mit eingesetzter Variable?::Mit f-String: `print(f"Hallo, {name}")` — das `f` vor dem Anführungszeichen nicht vergessen.

Wie verhinderst du den Zeilenumbruch bei `print`?::`print("Text", end="")`

---

## Strings

`.lower()` macht was?::Wandelt einen String komplett in Kleinbuchstaben um.

`.upper()` macht was?::Wandelt einen String komplett in GROSSBUCHSTABEN um.

`.strip()` macht was?::Entfernt Leerzeichen am Anfang und Ende eines Strings.

`.title()` macht was?::Macht den ersten Buchstaben jedes Wortes groß.

Wie ersetzt du in `text` alle Leerzeichen durch `...`?::`text.replace(" ", "...")`

Warum reicht `text.lower()` allein nicht?::String-Methoden verändern das Original **nicht**. Du musst das Ergebnis zurückgeben oder zuweisen: `text = text.lower()`

Wie hängst du zwei Strings zusammen?::Mit `+`: `"Hallo" + " " + "Welt"`

---

## Funktionen

Wie definierst du eine Funktion?::`def name(parameter):` — danach eingerückter Block.

Was macht `return`?::Gibt einen Wert an die aufrufende Stelle zurück und beendet die Funktion.

Unterschied zwischen `return` und `print`?
?
`print` **zeigt** etwas auf dem Bildschirm und gibt nichts zurück.
`return` **liefert einen Wert**, mit dem weitergerechnet werden kann — sichtbar wird er erst, wenn ihn jemand ausgibt.

Warum braucht Python die Einrückung?::Die Einrückung ersetzt die geschweiften Klammern anderer Sprachen — sie bestimmt, was zum Block gehört. Falsche Einrückung = Fehler.

---

## Problem Set 0

Was verlangt „Indoor Voice"?::Eingabe einlesen und komplett in Kleinbuchstaben ausgeben — `input()` + `.lower()`

Was verlangt „Playback Speed"?::Jedes Leerzeichen der Eingabe durch `...` ersetzen — `text.replace(" ", "...")`

Was verlangt „Making Faces"?::`:)` durch 🙂 und `:(` durch 🙁 ersetzen — und zwar in einer **eigenen Funktion** `convert`, die aus `main` aufgerufen wird.

Was ist der eigentliche Lernpunkt von „Making Faces"?::Nicht das Ersetzen, sondern: eine Funktion definieren, einen Wert zurückgeben, die Funktion aufrufen.
