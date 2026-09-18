# Prompts zum Weitergeben

Drei fertige Prompts: einer für ChatGPT (Qualitätsprüfung), einer für Claude Design
(Gestaltung), einer für Codex (fehlende Vokabeln ergänzen). Einfach kopieren und
einfügen.

---

## 1 — ChatGPT: Übersetzungen und Deutsch prüfen

**Wofür:** Die 449 Wörterbuch-Einträge und die Lektionstexte gegenprüfen.
**Wie benutzen:** Prompt einfügen, dann 30–50 Zeilen aus `vocab.json` darunter
kopieren. In Portionen arbeiten — nicht alle 449 auf einmal.

```
Du bist Lektor für einen Deutschkurs auf B1/B2-Niveau. Die Klasse besteht aus
Erwachsenen, die in Deutschland arbeiten. Ihre Erstsprachen umfassen Englisch,
Türkisch, Albanisch, Ukrainisch, Arabisch, Persisch, Spanisch, Französisch
und Italienisch.

Ich gebe dir Vokabeleinträge. Jeder Eintrag hat:
- de  = das deutsche Wort oder die Wendung
- en  = englische Bedeutung
- erk = einfache Erklärung auf Deutsch
- bsp = Beispielsatz auf Deutsch
- sq, tr, uk, ar, fa = Übersetzungen (Albanisch, Türkisch, Ukrainisch,
  Arabisch, Persisch)
- es, fr, it = Übersetzungen (Spanisch, Französisch, Italienisch); diese
  Felder gibt es ab der Lektion vom 17. September 2026

Die Übersetzungen wurden maschinell erstellt und sind NICHT von
Muttersprachlern geprüft. Genau das ist deine Aufgabe.

Prüfe für jeden Eintrag:
1. Trifft jede Übersetzung die Bedeutung, die "en" und "erk" beschreiben?
   Achte besonders auf Wörter mit mehreren Bedeutungen — die Übersetzung muss
   zu DIESEM Kontext passen, nicht zur häufigsten Bedeutung des Wortes.
2. Stimmt das Register? Der Kurs zielt auf Berufsalltag. Zu literarische,
   zu formelle oder veraltete Wörter sind ein Fehler, auch wenn sie
   sachlich richtig sind.
3. Ist der deutsche Beispielsatz grammatisch korrekt und natürlich? Würde
   das eine Kollegin im Büro wirklich so sagen?
4. Ist die deutsche Erklärung ("erk") einfacher als das erklärte Wort selbst?
   Wenn die Erklärung schwerer ist als das Stichwort, ist sie nutzlos.

Wichtig: Sei streng, aber melde nur echte Probleme. Wenn ein Eintrag in Ordnung
ist, schreibe nichts dazu. Ich brauche keine Bestätigung, sondern Fehler.

Format deiner Antwort — eine Zeile pro Problem:

  [de] | [Sprachcode] | falsch: "…" | besser: "…" | Grund: …

Am Ende: eine kurze Einschätzung pro Sprache, wie verlässlich die
Übersetzungen insgesamt wirken (z. B. "Türkisch: solide, 2 Fehler in 40" /
"Albanisch: mehrere unidiomatische Wendungen, würde ich komplett prüfen
lassen").

Hier sind die Einträge:

[HIER DIE ZEILEN AUS vocab.json EINFÜGEN]
```

### Variante: einen ganzen Lektionstext prüfen

```
Prüfe diesen deutschen Lesetext für einen B1/B2-Kurs für Erwachsene, die in
Deutschland arbeiten. Achte auf vier Dinge:

1. Sprachniveau — ist wirklich B1/B2, oder rutscht es stellenweise auf C1?
   Nenne konkrete Stellen, die zu schwer sind, und schlage einfachere
   Formulierungen vor.
2. Natürlichkeit — klingt es wie ein echter Zeitungstext oder wie
   Lehrbuchdeutsch? Zeige Stellen, die gestelzt wirken.
3. Grammatik und Rechtschreibung — alles, was falsch ist.
4. Sachliche Aussagen — markiere jede Zahl, jedes Datum und jeden Namen, den
   man nachprüfen sollte. Du musst nicht recherchieren, nur auflisten, was
   überprüft werden muss.

Lobe nichts. Liste nur, was ich ändern sollte.

Text:

[HIER DEN LESETEXT EINFÜGEN]
```

---

## 2 — Claude Design: Gestaltung der Website

**Wofür:** Eine Startseite und ein einheitliches Layout für die Kursseite.
**Wichtig:** Der Prompt nennt bewusst die technischen Grenzen. Ohne sie
entsteht ein Design, das die Sprachauswahl und die Übungen kaputt macht.

```
Ich unterrichte einen Deutschkurs (B1/B2) für Erwachsene, die in Deutschland
arbeiten. Dafür gibt es eine kleine statische Website, die ich als Ordner auf
einen Static-Host lege. Ich brauche Hilfe beim Design — die Funktionen stehen
schon.

WAS ES GIBT

1. Eine Archivseite (index.html): Liste aller Tageslektionen, neueste oben,
   nach Monat gruppiert. Dazu eine Kachel, die zum Wörterbuch führt.
2. Ein Wörterbuch (woerterbuch.html): 449 Einträge in einer Tabelle, mit
   Suchfeld und einem Dropdown für die Übersetzungssprache.
3. 62 Lektionsseiten, die neueren mit sechs Tabs: Lesetext, Vokabular,
   Ausdrücke, Grammatik, Übung, Lösungen.

DIE BESTEHENDE FARBWELT — bitte beibehalten, sie gefällt mir:

  Seitenhintergrund   #ffffff
  Inhaltskarten       #f6f2e9   (warmes Creme)
  Text                #2c2c2a
  Überschriften       #1c1c1c
  Graue Labels        #9a9488
  Zarte Linien        #eae5d6
  Datums-Badge        #f3e6c8 auf Text #7a6535
  Niveau-Badge        #e6f0e1 auf Text #3f6b3f
  Aktiver Tab         #2c2c2a mit weißem Text
  Richtige Antwort    #e6f0e1 / #3f6b3f
  Falsche Antwort     #f4e6e1 / #8a4b3c

  Schrift: Segoe UI / Helvetica / Arial. Wurzelgröße 14px, alles andere in rem.
  Charakter: ruhig, redaktionell, kompakt. Keine grellen Farben, keine
  Verläufe, keine Schatten außer sehr zarten.

WAS ICH VON DIR MÖCHTE

1. Eine echte Startseite, die es noch nicht gibt. Sie soll in wenigen Sekunden
   erklären, was das ist, und dann direkt zur heutigen Lektion und zum
   Wörterbuch führen. Zielgruppe: Erwachsene, die morgens zehn Minuten Zeit
   haben, nicht Studierende mit einem Semesterplan.
2. Einen besseren Aufbau der Archivseite. 50 Einträge als flache Liste werden
   bald unübersichtlich. Ich hätte gern Vorschläge — Gruppierung, Filter nach
   Thema, Suche, irgendetwas, das bei 200 Lektionen noch funktioniert.
3. Eine Kopfzeile, die auf allen Seiten gleich aussieht, mit Navigation
   zwischen Startseite, Archiv und Wörterbuch.

HARTE TECHNISCHE GRENZEN — bitte nicht verletzen

- Jede Seite muss eine einzige, in sich geschlossene HTML-Datei sein. CSS und
  JS inline. Keine externen Dateien, kein CDN, keine Frameworks, kein
  Build-Schritt, kein React, kein Tailwind. Reines HTML, CSS und Vanilla-JS.
- Die Seiten müssen auf dem Handy funktionieren. Viele meiner Teilnehmenden
  haben keinen Laptop. Die Vokabeltabelle bricht unter 760px in gestapelte
  Karten um; das muss so bleiben.
- Arabisch und Persisch werden von rechts nach links gesetzt. Übersetzungs-
  zellen in diesen Sprachen tragen dir="rtl" und müssen rechtsbündig bleiben.
- Das Sprach-Dropdown speichert die Wahl in localStorage unter dem Schlüssel
  dg-lang, gemeinsam über alle Seiten. Diese Mechanik darf nicht verändert
  werden.
- Die Tab-Navigation auf den Lektionsseiten schaltet eine CSS-Klasse "active"
  um und lädt die Seite nicht neu.
- Deutsch bleibt die Sprache der Oberfläche. Nur die Bedeutungsspalte im
  Vokabular wechselt die Sprache.

Fang mit der Startseite an. Zeig mir zuerst zwei oder drei unterschiedliche
Richtungen als Skizze, bevor du eine ausbaust — ich entscheide dann.
```

---

## 3 — Codex: fehlende Vokabeln aus den Juli-Lektionen ergänzen

**Status:** Am 16.09.2026 ausgeführt. 91 deduplizierte Einträge wurden ergänzt;
der Build meldet für die Juli-Lektionen keine fehlenden Vokabeln mehr. Der
Prompt bleibt als Ablaufdokumentation und für eine mögliche spätere Lücke hier.

**Wofür:** 14 ältere Lektionen (09.–23. Juli) wurden nachträglich aus
Markdown in das Website-Format konvertiert. Ihre Vokabeltabellen enthalten
rund 90 Wörter, die noch nicht in `vocab.json` stehen — deshalb fehlen dort
die Übersetzungen in vier der fünf Sprachen, und die Wörter tauchen im
Wörterbuch (`woerterbuch.html`) gar nicht auf.
**Wie benutzen:** Direkt in Codex (mit Repo-Zugriff) einfügen, im
Projektordner `Daily German`.

```
Lies zuerst AGENTS.md im Projektordner — dort stehen das Datenschema von
vocab.json, der Build-Ablauf und die Qualitätsanforderungen an
Übersetzungen. Halte dich an das dort beschriebene Schema.

Aufgabe: In vocab.json fehlen die Einträge für einen Teil der Vokabeln aus
den 14 Lektionen vom 09.–23. Juli 2026 (Dateien in lektionen/, Format
German_Lesson_2026-07-DD.html). Finde heraus, welche Wörter fehlen, ergänze
sie in vocab.json und schließe die Lücke.

1. Führe `python3 build_site.py` im Projektordner aus. `patch_vocab_lang.py`
   gibt für jede betroffene Lektion eine Zeile mit "unmatched: [...]" aus —
   das ist die genaue Liste der fehlenden deutschen Wörter pro Datum. Nutze
   diese Liste, erfinde sie nicht selbst.
2. Für jedes fehlende Wort: Die Spalten Deutsch/Englisch/Einfache
   Erklärung/Beispielsatz stehen bereits in der jeweiligen
   lektionen/German_Lesson_2026-07-DD.html-Datei, in der Vokabeltabelle des
   "vokabular"-Panels. Übernimm sie unverändert — erfinde keine neue
   Erklärung oder keinen neuen Beispielsatz.
3. Ergänze für jedes Wort die fünf Übersetzungen sq (Albanisch), tr
   (Türkisch), uk (Ukrainisch), ar (Arabisch), fa (Persisch), auf dem
   gleichen Niveau wie die bereits bestehenden Einträge: Berufsalltag-Register,
   keine literarischen oder veralteten Wörter, und passend zur konkreten
   Bedeutung im Kontext (viele deutsche Wörter sind mehrdeutig — die
   Übersetzung muss zur Bedeutung in "erk"/"bsp" passen, nicht zur
   häufigsten Wörterbuchbedeutung).
4. Neuer Eintrag pro Wort, exakt dieses Schema:
   { "de": "...", "en": "...", "erk": "...", "bsp": "...",
     "dates": ["2026-07-DD"], "sq": "...", "tr": "...", "uk": "...",
     "ar": "...", "fa": "..." }
   Ein Wort kann in mehreren der 14 Lektionen vorkommen (z. B. "sich einig
   sein", "befürchten") — dafür nur EINEN Eintrag anlegen und alle
   betroffenen Daten in "dates" sammeln, keine Duplikate.
5. Füge die neuen Einträge in vocab.json ein (die Reihenfolge im Array ist
   nicht streng alphabetisch und nicht wichtig — einfach anhängen reicht).
6. Führe danach `python3 build_site.py` erneut aus. Die "unmatched"-Zeilen
   für die 14 Juli-Lektionen sollten jetzt verschwunden oder deutlich
   kürzer sein. Wenn noch etwas übrig bleibt, sag mir was und warum.

Wichtig: Das sind, wie die bestehenden Einträge auch, KI-generierte
Übersetzungen — nicht von Muttersprachlern geprüft. Kennzeichne sie nicht
als geprüft und ändere nichts an der bestehenden Prüf-Kennzeichnung
(Hinweistext in woerterbuch.html). Fass website/ nicht direkt an — das ist
generierter Output, der Build erzeugt es neu.
```

---

## Eine Einschränkung, die man kennen sollte

ChatGPT prüft die Übersetzungen als weitere KI, nicht als Muttersprachler.
Für offensichtliche Fehler ist das nützlich; ein echtes Gütesiegel ist es
nicht. Zwei KI-Systeme können denselben Fehler machen, besonders bei
Albanisch und Persisch, wo beide weniger Trainingsdaten haben.

Verlässlich wird es erst, wenn die Teilnehmenden ihre eigene Sprache
durchsehen. Das dauert eine Unterrichtsstunde und ist gleichzeitig eine gute
Übung: Wer eine Übersetzung korrigiert, muss das deutsche Wort erst genau
verstehen.
