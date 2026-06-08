# archilog

## Vue d’ensemble
`archilog` est une application Flask de gestion d’entrées structurées. Elle offre :
- une interface web basée sur des templates Jinja,
- une API REST documentée avec Spectree,
- un CLI Click pour la gestion en ligne de commande,
- une base SQLite gérée avec SQLAlchemy.

## Architecture du projet
- `src/archilog/views/web_ui.py` : routes web, formulaires WTForms, authentification HTTP Basic.
- `src/archilog/views/api.py` : API REST sécurisée par token, validation `pydantic`/`spectree`.
- `src/archilog/views/cli.py` : commandes CLI Click (`init-db`, `create`, `get`, `get-all`, `update`, `delete`, `import_csv`, `export_csv`).
- `src/archilog/models.py` : modèle `Entry` et couche SQLAlchemy Core.
- `src/archilog/services.py` : import/export CSV.
- `src/archilog/views/__init__.py` : création et configuration de l’application Flask.

## Fonctionnalités
- Création, lecture, mise à jour et suppression d’entrées.
- Recherche d’entrées par UUID.
- Importation et exportation CSV.
- Authentification web HTTP Basic.
- Authentification API par token.
- Gestion d’erreurs et retour utilisateur via `flash`.

## Installation
### Prérequis
- Python 3.10+
- `pdm`
- fichier `dev.env` contenant `ARCHILOG_DATABASE_URL`.

Exemple :
```env
ARCHILOG_DATABASE_URL=sqlite:///data.db
```

### Installer les dépendances
```bash
pdm install
```

## Exécution
### Initialiser la base de données
```bash
pdm run archilog init-db
```

### Lancer l’application Flask
```bash
pdm run start
```

## Commandes CLI
```bash
pdm run archilog create --name "Nom" --amount 100 --category "Catégorie"
pdm run archilog get --id <UUID>
pdm run archilog get-all
pdm run archilog update --id <UUID> --name "Nouveau" --amount 120 --category "Autre"
pdm run archilog delete --id <UUID>
pdm run archilog import-csv "data.csv"
pdm run archilog export-csv "export.csv"
```

## Authentification
### Web
L’authentification web est codée en dur avec deux comptes :
- `admin` / `admin` (rôle `admin`)
- `user` / `user` (rôle `user`)

Ces utilisateurs sont définis dans `src/archilog/views/web_ui.py`.

### API
Le back-end API utilise des tokens statiques dans `src/archilog/views/api.py` :
- `admin-token`, rôle `admin`
- `user-token`, rôle `user`

Commande à faire pour utiliser API (Swagger via Curl) : 
`curl -H "Authorization: Bearer user-token" http://127.0.0.1:5000/api/user`
`curl -X DELETE -H "Authorization: Bearer admin-token" http://127.0.0.1:5000/api/user/"id"`
`curl -X POST http://127.0.0.1:5000/api/user -H "Authorization: Bearer admin-token" -H "Content-Type: application/json" -d "{\"name\":\"test\",\"amount\":10,\"category\":\"demo\"}"`

curl -X PUT http://127.0.0.1:5000/api/user/ae41f5abb3374fcd8597a04353fcacf9 \
-H "Authorization: Bearer admin-token" \
-H "Content-Type: application/json" \
-d '{"name":"test modifié","amount":20,"category":"demo update"}'


## Endpoints importants
### Routes web
- `/` : page d’accueil protégée
- `/entries` : liste des entrées
- `/entry?id=<UUID>` : consulter une entrée
- `/create` : créer une entrée (`admin` uniquement)
- `/update` : mettre à jour une entrée (`admin` uniquement)
- `/delete` : supprimer une entrée (`admin` uniquement)
- `/import_csv` : importer un CSV (`admin` uniquement)
- `/export_csv` : exporter un CSV

### API REST
- `GET /api/user` : liste toutes les entrées
- `GET /api/user/<id>` : récupère une entrée
- `POST /api/user` : crée une entrée (`admin` uniquement)
- `PUT /api/user/<id>` : met à jour une entrée (`admin` uniquement)
- `DELETE /api/user/<id>` : supprime une entrée (`admin` uniquement)
- `GET /api/export/entries` : export CSV
- `POST /api/import/entries` : import CSV (`admin` uniquement)


## Améliorations possibles
- ajout d’une table `User` et d’une authentification plus robuste,
- implémentation d’un vrai système d’inscription,
- migration vers JWT ou Flask-Login,
- meilleure gestion des erreurs CSV,
