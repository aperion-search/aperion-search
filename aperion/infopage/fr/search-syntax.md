# Syntaxe de recherche

Aperion Search propose une syntaxe de recherche qui vous permet de modifier les catégories, moteurs, langues, et plus encore. Consultez les {{link('preferences', 'préférences')}} pour la liste des moteurs, catégories et langues.

## `!` Sélectionner moteur et catégorie

Pour définir les noms de catégorie et/ou de moteur, utilisez le préfixe `!`. Voici quelques exemples :

- Rechercher sur Wikipedia le terme **paris** :

  - {{search('!wp paris')}}
  - {{search('!wikipedia paris')}}

- Rechercher dans la catégorie **map** le terme **paris** :

  - {{search('!map paris')}}

- Recherche d’images

  - {{search('!images Wau Holland')}}

Les abréviations des moteurs et des langues sont également acceptées. Les modificateurs moteur/catégorie peuvent être combinés et sont inclusifs. Par exemple, {{search('!map !ddg !wp paris')}} recherche dans la catégorie map et interroge DuckDuckGo ainsi que Wikipedia pour **paris**.

## `:` Sélectionner la langue

Pour appliquer un filtre de langue, utilisez le préfixe `:`. Voici un exemple :

- Rechercher sur Wikipedia avec une langue personnalisée :

  - {{search(':fr !wp Wau Holland')}}

## `!!<bang>` Bangs externes

Aperion Search prend en charge les bangs externes de [DuckDuckGo]. Pour accéder directement à une page de recherche externe, utilisez le préfixe `!!`. Par exemple :

- Rechercher sur Wikipedia avec une langue personnalisée :

  - {{search('!!wfr Wau Holland')}}

Veuillez noter que votre recherche sera effectuée directement sur le moteur externe. Aperion Search ne peut pas protéger votre vie privée dans ce cas.

[DuckDuckGo] : https://duckduckgo.com/bang

## `!!` redirection automatique

En incluant `!!` dans votre requête de recherche (séparé par des espaces), vous serez automatiquement redirigé vers le premier résultat. Ce comportement est comparable à la fonction « Je me sens chanceux » de DuckDuckGo. Par exemple :

- Rechercher une requête et être redirigé vers le premier résultat

  - {{search('!! Wau Holland')}}

Gardez à l’esprit que le résultat vers lequel vous êtes redirigé ne peut pas être vérifié quant à sa fiabilité et qu’Aperion Search ne peut pas protéger votre vie privée lors de l’utilisation de cette fonction. Utilisez-la à vos risques et périls.

## Requêtes spéciales

Dans la page {{link('preferences', 'préférences')}}, vous trouverez des mots-clés pour des _requêtes spéciales_. Voici quelques exemples :

- Générer un UUID aléatoire

  - {{search('random uuid')}}

- Calculer la moyenne

  - {{search('avg 123 548 2.04 24.2')}}

- Afficher l’_user agent_ de votre navigateur (à activer)

  - {{search('user-agent')}}

- Convertir des chaînes en différents condensés de hachage (à activer)

  - {{search('md5 lorem ipsum')}}
  - {{search('sha512 lorem ipsum')}}