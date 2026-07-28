# Suchsyntax

Aperion Search verfügt über eine Suchsyntax, mit der Sie Kategorien,
Suchmaschinen, Sprachen und mehr anpassen können.  Unter {{link(‚preferences‘, ‚preferences‘)}} finden Sie
eine Liste der Suchmaschinen, Kategorien und Sprachen.

## `!` Suchmaschine und Kategorie auswählen

Um Kategorie- und/oder Suchmaschinennamen festzulegen, verwenden Sie das Präfix `!`.  Hier einige Beispiele:

- Suche in Wikipedia nach **Paris**:

  - {{search(‚!wp Paris‘)}}
  - {{search(‚!wikipedia Paris‘)}}

- Suche in der Kategorie **Karte** nach **Paris**:

  - {{search(‚!map Paris‘)}}

- Bildersuche

- {{search(‚!images Wau Holland‘)}}

Abkürzungen der Suchmaschinen und Sprachen werden ebenfalls akzeptiert.  Suchmaschinen-/Kategorienmodifikatoren
sind verkettbar und inklusiv.  Beispielsweise sucht {{search('!map !ddg !wp
paris')}} in der Kategorie „map“ und durchsucht DuckDuckGo und Wikipedia nach **paris**.

## `:` Sprache auswählen

Um einen Sprachfilter auszuwählen, verwenden Sie das Präfix `:`.  Ein Beispiel:

- Wikipedia mit einer benutzerdefinierten Sprache durchsuchen:

- {{search(‚:fr !wp Wau Holland‘)}}

## `!!<bang>` Externe Bangs

Aperion Search unterstützt die externen Bangs von [DuckDuckGo].  Um direkt zu einer
externen Suchseite zu springen, verwenden Sie das Präfix `!!`.  Ein Beispiel:

- Wikipedia mit einer benutzerdefinierten Sprache durchsuchen:

  - {{search(‚!!wfr Wau Holland‘)}}

Bitte beachten Sie, dass Ihre Suche direkt in der externen Suchmaschine durchgeführt wird.
Aperion Search kann Ihre Privatsphäre dabei nicht schützen.

[DuckDuckGo]: https://duckduckgo.com/bang

## `!!` Automatische Weiterleitung

Wenn Sie `!!` mit

Übersetzt mit DeepL.com (kostenlose Version)