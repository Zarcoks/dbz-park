# Dragon Ball Park

Application Django de billetterie pour un parc d'attractions Dragon Ball Z.

Structure de code reprise de `bonjour_plant` : un projet `core/` (settings,
urls) et une app `park_management/` organisée en pages (`pages/<nom>/` avec
`urls.py`, `views.py`, `forms.py`).

Le style suit la même approche : Bootstrap et Bootstrap Icons servis depuis
`static/` (pas de CDN), plus une feuille `dbz-park.css` qui pose les couleurs du
parc. Le gabarit `park_management/templates/park_management/index.html` porte
l'en-tête et le menu du compte, en haut à droite ; toutes les pages en héritent.

## Lancement

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Fonctionnalités actuelles

- Un visiteur peut créer un compte (`/compte/inscription/`) et se connecter (`/compte/connexion/`).
- **Mes billets** (`/`) : les billets ne sont pas créés ici. La billetterie les écrit
  dans la même base, le visiteur en reçoit le numéro par mail, et cette page ne fait
  que rattacher un billet libre à son compte — un numéro, et rien d'autre. Le rôle
  (`normal`, `sayan`, `super_sayan`) est fixé à l'achat et suit le billet.
  Un numéro inconnu ou déjà pris est refusé, sans dire par qui.
- **Attractions** (`/attractions/`) : les attractions du parc, avec leur photo (une
  illustration par défaut si elle manque) et leur capacité maximale.
- **État d'une attraction** (`AttractionState`) : le direct d'une attraction —
  capacité réelle, durée minimale et maximale d'un tour, et l'heure du dernier
  relevé. Un seul état par attraction, réécrit au fil de l'eau plutôt qu'empilé.
  La capacité maximale reste sur l'attraction et n'est pas recopiée dans l'état.
  Rien de tout cela n'apparaît encore aux visiteurs : le modèle n'est visible que
  dans `/admin/`.
- Les comptes admin (`is_staff`/`is_superuser`, via `python manage.py createsuperuser`) ont accès à `/admin/` mais n'ont pas de fonctionnalité dédiée pour l'instant.

Pour se donner de quoi essayer, `/admin/` permet de créer des billets libres (numéro
+ rôle, sans visiteur) et des attractions, comme le ferait la billetterie.
