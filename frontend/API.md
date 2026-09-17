# Contrat d'API — ce que le front attend du back

Le front est déjà écrit contre ces formes. Le back n'a qu'à les respecter :
aucune modification du front ne sera nécessaire, il suffira de passer
`VITE_USE_MOCK=false`.

Toutes les adresses sont préfixées par `VITE_API_URL` (par défaut `/api`).
Les dates sont en **ISO 8601** (`2026-09-17T14:05:00`), c'est le front qui les
met en forme.

## Authentification

Le front envoie `Authorization: Bearer <jeton>` sur chaque appel, dès qu'un
jeton existe. Un jeton plutôt qu'un cookie de session : le back reste **sans
état**, donc n'importe quel serveur derrière le load balancer peut répondre,
sans sticky sessions.

En cas d'erreur, le back répond avec un code HTTP ≥ 400 et un corps
`{ "detail": "Le message à montrer au visiteur." }` — c'est ce texte que le
front affiche tel quel.

---

## Comptes

### `POST /auth/inscription/`
```jsonc
// envoi
{ "username": "goku", "email": "goku@dbz.fr", "password1": "…", "password2": "…" }
// réponse
{ "token": "…", "user": { "id": 1, "username": "goku", "is_staff": false } }
```

### `POST /auth/connexion/`
```jsonc
// envoi
{ "username": "goku", "password": "…" }
// réponse
{ "token": "…", "user": { "id": 1, "username": "goku", "is_staff": false } }
```

### `POST /auth/deconnexion/`
Aucun corps. Réponse `204`.

### `GET /auth/moi/`
Qui est connecté, d'après le jeton. Sert au rechargement de la page.
```jsonc
{ "id": 1, "username": "goku", "is_staff": false }
```

---

## Billets

### `GET /billets/`
Les billets du visiteur connecté.
```jsonc
[
  {
    "id": 1,
    "numero": "DBZ-0001",
    "role": "super_sayan",          // normal | sayan | super_sayan
    "role_display": "Super Saiyan", // le libellé affiché
    "assigned_at": "2026-09-17T09:12:00"
  }
]
```
`role` sert à la couleur (classes CSS `ticket-<role>` et `role-badge-<role>`),
`role_display` au texte.

### `POST /billets/assigner/`
```jsonc
// envoi
{ "numero": "DBZ-0003" }
// réponse : le billet, même forme que ci-dessus
```
Un numéro inconnu et un numéro déjà pris doivent donner **la même** erreur : on
ne dit pas à qui appartient un billet.

---

## Attractions & files

### `GET /attractions/`
Reprend le contexte `cards` de `AttractionList` : chaque attraction avec ce que
le visiteur y a en cours.
```jsonc
[
  {
    "id": 1,
    "name": "La Salle du Temps",
    "photo_url": "https://…/attraction.jpg", // "" si pas de photo
    "max_people": 50,
    "people_inside": 12,
    "duration_range": "2 – 5 min",           // déjà mis en forme par le back

    // Le visiteur est dans l'attraction — sinon null.
    "visit": { "billet": { … }, "entered_at": "2026-09-17T14:02:00" },

    // Il tient une place dans la file — sinon null.
    "entry": {
      "id": 7,
      "billet": { … },
      "joined_at": "2026-09-17T13:40:00",
      "is_ready": true,
      "ready_at": "2026-09-17T14:00:00",
      "ready_expired": false   // calculé par le back, pas par le front
    },

    // Sa position, uniquement tant qu'il n'est pas appelé — sinon null.
    "rank": 3,

    // Le billet qui partirait s'il rejoignait la file — null s'il n'en a aucun
    // de disponible, ou s'il a déjà une place ou une présence ici.
    "billet": { "id": 1, "numero": "DBZ-0001", "role": "super_sayan", "role_display": "Super Saiyan" }
  }
]
```

Les quatre cas s'excluent, et le front les lit dans cet ordre :
`visit` → `entry` appelée → `entry` expirée → `entry` en attente → `billet`.

### `POST /attractions/<id>/file/rejoindre/`
Aucun corps. Le back choisit lui-même le meilleur billet du visiteur. `204`.

### `POST /files/<entry_id>/quitter/`
Aucun corps. `204`.

### `POST /files/<entry_id>/valider/`
Aucun corps. `204`. Refuse (`400`) si le tour n'est pas venu ou s'il est passé.

---

## Console (réservée à `is_staff`)

### `GET /console/`
```jsonc
[
  {
    "attraction": { "id": 1, "name": "La Salle du Temps", "max_people": 50, "max_ready_waiting": 300 },
    "inside": 12,
    "waiting": 34,
    "ready": [
      {
        "id": 7,
        "username": "goku",
        "billet": { "id": 1, "numero": "DBZ-0001", "role": "super_sayan", "role_display": "Super Saiyan" },
        "ready_at": "2026-09-17T14:00:00",
        "ready_expired": false
      }
    ]
  }
]
```
Une attraction sans personne d'appelé est renvoyée quand même, avec `ready: []`.

### `POST /console/places/<entry_id>/accepter/`
Le visiteur entre. `204`. Contrairement à la validation côté visiteur, une place
au **délai dépassé peut être acceptée** : c'est l'admin qui décide.

### `POST /console/places/<entry_id>/refuser/`
La place est retirée. `204`.

---

## Réservé aux points d'accès qui n'existent pas encore

Ces routes ne sont pas appelées par le front actuel, mais le SPEC les prévoit.
Elles viendront s'ajouter à `src/api/endpoints.js` sans rien casser :
jauge globale du parc, QR code dynamique, incidents et notifications broadcast,
KPI de supervision.
