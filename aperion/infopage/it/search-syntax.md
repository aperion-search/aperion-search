# Sintassi di ricerca

Aperion Search è dotato di una sintassi di ricerca che consente di modificare le categorie, i
motori, le lingue e altro ancora.  Vedere {{link(‘preferences’, ‘preferences’)}} per
l'elenco dei motori, delle categorie e delle lingue.

## `!` Selezionare motore e categoria

Per impostare i nomi delle categorie e/o dei motori, utilizzare il prefisso `!`.  Ecco alcuni esempi:

- Cerca **parigi** su Wikipedia:

- {{search(‘!wp parigi’)}}
- {{search(‘!wikipedia parigi’)}}

- Cerca **parigi** nella categoria **mappa**:

- {{search(‘!mappa parigi’)}}

- Ricerca immagini

- {{search(‘!images Wau Holland’)}}

Sono accettate anche le abbreviazioni dei motori e delle lingue.  I modificatori di motore/categoria
sono concatenabili e inclusivi.  Ad esempio, {{search('!map !ddg !wp
paris')}} cerca nella categoria map e cerca **paris** su DuckDuckGo e Wikipedia.

## `:` Seleziona lingua

Per selezionare un filtro lingua, usa il prefisso `:`.  Ad esempio:

- Cerca su Wikipedia con una lingua personalizzata:

- {{search(‘:fr !wp Wau Holland’)}}

## `!!<bang>` Bang esterni

Aperion Search supporta i bang esterni da [DuckDuckGo].  Per passare direttamente a una
pagina di ricerca esterna, usa il prefisso `!!`.  Ad esempio:

- Cerca su Wikipedia con una lingua personalizzata:

- {{search(‘!!wfr Wau Holland’)}}

Si prega di notare che la ricerca verrà eseguita direttamente nel motore di ricerca esterno.
  Aperion Search non può proteggere la privacy dell'utente in questo caso.

[DuckDuckGo]: https://duckduckgo.com/bang

## `!!` reindirizzamento automatico

Quando si include `!!` con