# API contract — what the front expects from the back

The front is already written against these shapes. The back only has to respect
them: no front-end change will be needed, just flip `VITE_USE_MOCK=false`.

Every path is prefixed with `VITE_API_URL` (default `/api`).
Dates are **ISO 8601** (`2026-09-17T14:05:00`); formatting is the front's job.

## Authentication

The front sends `Authorization: Bearer <token>` on every call, as soon as a
token exists. The token is a **signed JWT**: the back stores nothing and only
checks the signature, so any server behind the load balancer can answer, with no
sticky sessions.

The price of that choice: a token cannot be revoked. There is therefore **no
logout route** — logging out means the front dropping its token, and the token
itself stops being accepted when it expires. A stolen token stays valid until
then, which is why the lifetime is one park day, not one year.

## Only two status codes

To keep the back simple, there are exactly two possible answers.

| Code | When |
| ---- | ---- |
| `200 OK` | it worked. The body is the one described under the route (nothing at all when the route has no data to return). |
| `400 Bad Request` | anything else. Body: `{ "detail": "The message to show the visitor." }` — the front prints that text as is. |

So a `400` covers all three families of refusal, and the only thing that tells
them apart is `detail`:

1. **Not logged in.** Every route except signup and login needs a valid token.
   No token, unknown token, expired token → `400`. Applies to reading tickets,
   buying one, joining a queue, opening the console — everything.
2. **Malformed request.** A missing field, a wrong type, an unparseable body, an
   unknown value (`role` that is not `normal | sayan | super_sayan`) → `400`.
3. **The action is not allowed.** Right shape, right token, but the business
   rules say no: not a staff account, a ticket that is not yours, a place that
   does not exist, a turn that has not come. → `400`.

Two consequences worth stating, since a single code carries everything:

- **Write a useful `detail`.** It is the only thing the visitor will see, so it
  must say what to do, not what went wrong internally.
- **Never reveal what the caller is not entitled to know.** An id that does not
  exist and an id that belongs to someone else must return the *same* `detail`;
  otherwise the API becomes a way to probe other people's tickets.

---

## Accounts

### `POST /auth/signup/`
```jsonc
// request
{ "username": "goku", "email": "goku@dbz.fr", "password1": "…", "password2": "…" }
// response
{ "token": "…", "user": { "id": 1, "username": "goku", "is_staff": false } }
```

| Code | When |
| ---- | ---- |
| `200 OK` | account created, the token is usable right away. |
| `400 Bad Request` | a missing field, the two passwords differ, or that username (or email) is already taken. |

### `POST /auth/login/`
```jsonc
// request
{ "username": "goku", "password": "…" }
// response
{ "token": "…", "user": { "id": 1, "username": "goku", "is_staff": false } }
```

| Code | When |
| ---- | ---- |
| `200 OK` | credentials accepted. |
| `400 Bad Request` | wrong username *or* wrong password — one single `detail` for both, so the answer never confirms that an account exists. |

### `GET /auth/me/`
Who is logged in, according to the token. Used when the page is reloaded.
```jsonc
{ "id": 1, "username": "goku", "is_staff": false }
```

| Code | When |
| ---- | ---- |
| `200 OK` | the account behind the token. |
| `400 Bad Request` | no valid token — the front drops the one it had and shows the login page. |

---

## Tickets

A ticket is a `ticket` row: a unique `numero`, a `role` fixed at purchase time,
and a `user_id` that is `null` as long as nobody has claimed it.

**Every route in this section requires a logged-in visitor**, and answers a
`400` when there is no valid token. Every ticket is usable as soon as it exists:
there is no payment step, and no unpaid state.

### `GET /tickets/`
**Staff only.** Every ticket in the park, with whoever holds it — the view the
counter and the support desk need to answer « à qui est ce billet ? ».
```jsonc
[
  {
    "id": 1,
    "numero": "DBZ-0001",
    "role": "super_sayan",   // normal | sayan | super_sayan
    "created_at": "2026-09-17T09:12:00",
    "user": { "id": 1, "username": "goku" }   // null while nobody has claimed it
  }
]
```
This is the one route that shows who owns what. Everywhere else the API is built
so a visitor cannot learn anything about another visitor's tickets — which is
exactly why this one is closed to anyone but the staff.

| Code | When |
| ---- | ---- |
| `200 OK` | every ticket, assigned or not, `[]` if the park has none. |
| `400 Bad Request` | not logged in, or logged in without `is_staff` — the same `detail` for both, as on the console. |

### `GET /user/<user_id>/tickets/`
The tickets held by one visitor. Readable by **that visitor, or by a staff
account** — nobody else, and the refusal does not say which of the two reasons
applies.
```jsonc
[
  {
    "id": 1,
    "numero": "DBZ-0001",
    "role": "super_sayan",
    "created_at": "2026-09-17T09:12:00"
  }
]
```
`role` is the only fare field: it drives the colour (CSS classes `ticket-<role>`
and `role-badge-<role>`) and the label, which the front spells out.

| Code | When |
| ---- | ---- |
| `200 OK` | the list, `[]` if that visitor owns none. |
| `400 Bad Request` | not logged in; or `<user_id>` is somebody else and the caller is not staff; or no such user — those last two share one `detail`, so the route cannot be used to find out which accounts exist. |

### `POST /tickets/`
Buys a ticket from the app: creates the `ticket` row, already attached to the
caller and immediately usable.
```jsonc
// request
{ "role": "sayan" }   // normal | sayan | super_sayan
// response
{
  "id": 12,
  "numero": "DBZ-0042",   // generated by the back, never sent by the front
  "role": "sayan",
  "created_at": "2026-09-17T10:04:00"
}
```

| Code | When |
| ---- | ---- |
| `200 OK` | the ticket exists and can join a queue right away. |
| `400 Bad Request` | not logged in (a ticket has to belong to somebody), `role` missing or not one of the three values, or that role is sold out for the day. |

### `POST /tickets/assign/`
Attaches a ticket bought elsewhere (counter, website) to the account, from its
number alone.
```jsonc
// request
{ "numero": "DBZ-0003" }
// response: the ticket, same shape as `GET /tickets/`
```

| Code | When |
| ---- | ---- |
| `200 OK` | the ticket now belongs to the visitor. |
| `400 Bad Request` | not logged in, `numero` missing, or the number is unknown **or** already taken — those last two share the very same `detail`: we never reveal who owns a ticket. |

---

## Attractions & queues

### `GET /attractions/`
The catalogue, and nothing else: every field below belongs to the attraction
itself. What *this* visitor has going on there — a place in the queue, a
position, a visit — is not here; it is read from the queue routes.
```jsonc
[
  {
    "id": 1,
    "name": "La Salle du Temps",
    "photo_url": "https://…/attraction.jpg", // "" when there is no photo
    "max_people": 50,
    "people_inside": 12,
    "avg_duration": 120                      // seconds, one ride
  }
]
```
`people_inside` is a counter carried by the attraction, not a count made at read
time: it is the back's job to raise it on entry and lower it on exit, and the
pair `people_inside` / `max_people` is what says whether the attraction is full.

| Code | When |
| ---- | ---- |
| `200 OK` | the list, `[]` if the park has no attraction yet. |
| `400 Bad Request` | not logged in. |

### `POST /attractions/<id>/queue/join/`
No request body, no response body. The back picks the visitor's best ticket
itself (super saiyan, then saiyan, then normal).

| Code | When |
| ---- | ---- |
| `200 OK` | the place is taken. |
| `400 Bad Request` | not logged in; unknown attraction; the visitor already holds a place or is already inside here (one ticket, one place per attraction); no usable ticket (none owned, or all already engaged elsewhere); or the queue is closed (after 19:00). |

### `GET /queue/<entry_id>/position/`
How many people are ahead, this place included: `1` means *next in line*. The
front polls it to refresh the wait without reloading the whole attraction list.
```jsonc
{ "position": 3 }
```

| Code | When |
| ---- | ---- |
| `200 OK` | the current position, recomputed on the fly — a super saiyan joining ahead makes it grow. |
| `400 Bad Request` | not logged in, or the place is unknown **or** not this visitor's — same `detail` for both, since a position tells how busy a queue is. |

### `POST /queue/<entry_id>/leave/`
No request body, no response body. Voluntary withdrawal: the place disappears
and the queue moves up.

| Code | When |
| ---- | ---- |
| `200 OK` | the place is released. |
| `400 Bad Request` | not logged in, or the place is unknown or not this visitor's. |

### `POST /queue/<entry_id>/validate/`
No request body, no response body. The visitor shows up after being called: the
place is deleted and a visit takes over, in the same transaction.

| Code | When |
| ---- | ---- |
| `200 OK` | the visitor is inside. |
| `400 Bad Request` | not logged in; the place is unknown or not theirs; their turn has not come yet (`is_ready` is false); or it has passed (`max_seconds_allowing_ready` elapsed since `ready_at`). |

---

## Console (staff only)

Every route below needs a token **and** an `is_staff` account. A visitor who is
merely logged in is refused exactly like someone who sent no token at all: a
plain `400`. Nothing in the answer says whether the console exists, what it
holds, or what would have been needed to open it.

### `GET /console/`
```jsonc
[
  {
    "attraction": { "id": 1, "name": "La Salle du Temps", "max_people": 50 },
    "inside": 12,
    "waiting": 34,
    "ready": [
      {
        "id": 7,
        "username": "goku",
        "ticket": { "id": 1, "numero": "DBZ-0001", "role": "super_sayan" },
        "ready_at": "2026-09-17T14:00:00",
        "max_seconds_allowing_ready": 300,
        "ready_expired": false
      }
    ]
  }
]
```
An attraction with nobody called is still returned, with `ready: []`.

| Code | When |
| ---- | ---- |
| `200 OK` | one row per attraction. |
| `400 Bad Request` | not logged in, or logged in without `is_staff`. |

### `POST /console/entries/<entry_id>/accept/`
The visitor goes in. No request body, no response body.

| Code | When |
| ---- | ---- |
| `200 OK` | the place becomes a visit. Unlike the visitor-side validation, an **expired** place can be accepted: the admin decides. |
| `400 Bad Request` | not a logged-in staff account; unknown place; or the attraction is full (`people_inside` = `max_people`) and someone has to come out first. |

### `POST /console/entries/<entry_id>/refuse/`
The place is removed. No request body, no response body.

| Code | When |
| ---- | ---- |
| `200 OK` | the place is gone and the queue moves up. |
| `400 Bad Request` | not a logged-in staff account, or unknown place. |

---

## Reserved for endpoints that do not exist yet

These routes are not called by the current front, but the SPEC plans for them.
They will be added to `src/api/endpoints.js` without breaking anything:
park-wide crowd gauge, dynamic QR code, incidents and broadcast notifications,
supervision KPIs.
