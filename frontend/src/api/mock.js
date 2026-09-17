/**
 * Un faux back, en mémoire, pour que le front tourne avant que l'API existe.
 *
 * Il rend exactement les formes décrites dans `frontend/API.md` : le jour où le
 * vrai back répond, on passe VITE_USE_MOCK à false et rien d'autre ne bouge.
 * Les données repartent de zéro à chaque rechargement de la page — c'est une
 * maquette, pas une base.
 */

import { getToken } from './client'

export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

const ROLE_LABELS = {
  normal: 'Normal',
  sayan: 'Saiyan',
  super_sayan: 'Super Saiyan',
}

// Du meilleur rôle au plus commun : c'est cet ordre qui décide du billet joué.
const ROLE_PRIORITY = ['super_sayan', 'sayan', 'normal']

// ── Les données de départ ───────────────────────────────────────────────────

const db = {
  // Deux comptes pour essayer : un visiteur et un admin.
  users: [
    { id: 1, username: 'goku', password: 'kamehameha', is_staff: false },
    { id: 2, username: 'admin', password: 'admin', is_staff: true },
  ],
  billets: [
    { id: 1, user_id: 1, numero: 'DBZ-0001', role: 'super_sayan', assigned_at: '2026-09-17T09:12:00' },
    { id: 2, user_id: 1, numero: 'DBZ-0002', role: 'normal', assigned_at: '2026-09-17T09:30:00' },
    // Billet libre, pour essayer l'assignation depuis « Mes billets ».
    { id: 3, user_id: null, numero: 'DBZ-0003', role: 'sayan', assigned_at: null },
  ],
  attractions: [
    { id: 1, name: 'La Salle du Temps', photo_url: '', max_people: 50, min_minutes: 2, max_minutes: 5, max_ready_waiting: 300 },
    { id: 2, name: 'Le Vaisseau de Freezer', photo_url: '', max_people: 30, min_minutes: 3, max_minutes: 6, max_ready_waiting: 180 },
    { id: 3, name: 'Le Palais de Kaio', photo_url: '', max_people: 20, min_minutes: 1, max_minutes: 2, max_ready_waiting: 240 },
  ],
  entries: [],
  visits: [],
  nextId: 100,
}

let currentUser = null

// ── Petits utilitaires ──────────────────────────────────────────────────────

/** Simule le temps d'un aller-retour réseau, pour voir les états de chargement. */
const wait = () => new Promise((resolve) => setTimeout(resolve, 250))

const nextId = () => db.nextId++

const fail = (message) => {
  throw new Error(message)
}

function publicUser(user) {
  return { id: user.id, username: user.username, is_staff: user.is_staff }
}

function publicBillet(billet) {
  return {
    id: billet.id,
    numero: billet.numero,
    role: billet.role,
    role_display: ROLE_LABELS[billet.role],
    assigned_at: billet.assigned_at,
  }
}

/** « 2 – 5 min », comme `Attraction.duration_range()` côté Django. */
function durationRange(attraction) {
  const { min_minutes, max_minutes } = attraction
  return min_minutes === max_minutes
    ? `${min_minutes} min`
    : `${min_minutes} – ${max_minutes} min`
}

const peopleInside = (attractionId) =>
  db.visits.filter((v) => v.attraction_id === attractionId).length

/** Le délai de présentation est-il dépassé ? Voir `QueueEntry.ready_expired()`. */
function readyExpired(entry) {
  if (!entry.ready_at) return false
  const attraction = db.attractions.find((a) => a.id === entry.attraction_id)
  const secondsSince = (Date.now() - new Date(entry.ready_at).getTime()) / 1000
  return secondsSince > attraction.max_ready_waiting
}

/** Le meilleur billet libre du visiteur pour cette attraction, ou null. */
function bestBillet(attractionId) {
  const engaged = new Set([
    ...db.entries.filter((e) => e.attraction_id === attractionId).map((e) => e.billet_id),
    ...db.visits.filter((v) => v.attraction_id === attractionId).map((v) => v.billet_id),
  ])
  const mine = db.billets.filter((b) => b.user_id === currentUser?.id && !engaged.has(b.id))
  mine.sort((a, b) => ROLE_PRIORITY.indexOf(a.role) - ROLE_PRIORITY.indexOf(b.role))
  return mine[0] ?? null
}

const billetOf = (id) => db.billets.find((b) => b.id === id)

/** Le meilleur billet, prêt à être renvoyé — ou null si le visiteur n'en a pas. */
function bestBilletPayload(attractionId) {
  const billet = bestBillet(attractionId)
  return billet ? publicBillet(billet) : null
}

// ── Les réponses ────────────────────────────────────────────────────────────

export const mock = {
  // Comptes
  async login({ username, password }) {
    await wait()
    const user = db.users.find((u) => u.username === username && u.password === password)
    if (!user) fail('Identifiants incorrects.')
    currentUser = user
    return { token: `faux-jeton-${user.id}`, user: publicUser(user) }
  },

  async signup({ username, password }) {
    await wait()
    if (db.users.some((u) => u.username === username)) fail('Ce nom est déjà pris.')
    const user = { id: nextId(), username, password, is_staff: false }
    db.users.push(user)
    currentUser = user
    return { token: `faux-jeton-${user.id}`, user: publicUser(user) }
  },

  async logout() {
    await wait()
    currentUser = null
    return null
  },

  // Au rechargement de la page, la mémoire du faux back est repartie de zéro :
  // on retrouve le visiteur depuis son jeton, comme le vrai back le ferait.
  async me() {
    await wait()
    if (!currentUser) {
      const id = Number(getToken()?.replace('faux-jeton-', ''))
      currentUser = db.users.find((u) => u.id === id) ?? null
    }
    if (!currentUser) fail('Non connecté.')
    return publicUser(currentUser)
  },

  // Billets
  async billets() {
    await wait()
    return db.billets.filter((b) => b.user_id === currentUser?.id).map(publicBillet)
  },

  async assignBillet({ numero }) {
    await wait()
    const billet = db.billets.find((b) => b.numero === numero)
    // Un numéro inconnu et un numéro déjà pris donnent la même réponse : on ne
    // dit pas à qui appartient un billet.
    if (!billet || billet.user_id !== null) fail('Ce numéro de billet est introuvable.')
    billet.user_id = currentUser.id
    billet.assigned_at = new Date().toISOString()
    return publicBillet(billet)
  },

  // Attractions
  async attractions() {
    await wait()
    return db.attractions.map((attraction) => {
      const mine = (row) =>
        row.attraction_id === attraction.id && billetOf(row.billet_id)?.user_id === currentUser?.id

      const visit = db.visits.find(mine)
      const entry = db.entries.find(mine)

      return {
        id: attraction.id,
        name: attraction.name,
        photo_url: attraction.photo_url,
        max_people: attraction.max_people,
        people_inside: peopleInside(attraction.id),
        duration_range: durationRange(attraction),
        visit: visit
          ? { billet: publicBillet(billetOf(visit.billet_id)), entered_at: visit.entered_at }
          : null,
        entry: entry
          ? {
              id: entry.id,
              billet: publicBillet(billetOf(entry.billet_id)),
              joined_at: entry.joined_at,
              is_ready: entry.is_ready,
              ready_at: entry.ready_at,
              ready_expired: readyExpired(entry),
            }
          : null,
        // Le rang ne vaut que tant que le billet n'est pas appelé.
        rank:
          entry && !entry.is_ready
            ? db.entries.filter(
                (e) => e.attraction_id === attraction.id && e.joined_at < entry.joined_at,
              ).length + 1
            : null,
        // Le billet qui partirait si le visiteur rejoignait la file : montré
        // avant de cliquer, pour qu'il sache lequel est joué.
        billet: entry || visit ? null : bestBilletPayload(attraction.id),
      }
    })
  },

  async joinQueue(attractionId) {
    await wait()
    const billet = bestBillet(attractionId)
    if (!billet) fail('Aucun de vos billets ne peut rejoindre cette file.')
    db.entries.push({
      id: nextId(),
      attraction_id: attractionId,
      billet_id: billet.id,
      joined_at: new Date().toISOString(),
      // Pour la maquette, le premier de la file est appelé tout de suite ; côté
      // back, c'est l'attraction qui décidera.
      is_ready: db.entries.filter((e) => e.attraction_id === attractionId).length === 0,
      ready_at:
        db.entries.filter((e) => e.attraction_id === attractionId).length === 0
          ? new Date().toISOString()
          : null,
    })
    return null
  },

  async leaveQueue(entryId) {
    await wait()
    db.entries = db.entries.filter((e) => e.id !== entryId)
    return null
  },

  async validateQueue(entryId) {
    await wait()
    const entry = db.entries.find((e) => e.id === entryId)
    if (!entry) fail('Cette place n\'existe plus.')
    if (!entry.is_ready) fail("Votre tour n'est pas encore venu.")
    if (readyExpired(entry)) fail('Votre tour est passé : la place a été rendue à la file.')
    db.visits.push({
      id: nextId(),
      attraction_id: entry.attraction_id,
      billet_id: entry.billet_id,
      entered_at: new Date().toISOString(),
    })
    db.entries = db.entries.filter((e) => e.id !== entryId)
    return null
  },

  // Console
  async console() {
    await wait()
    return db.attractions.map((attraction) => ({
      attraction: {
        id: attraction.id,
        name: attraction.name,
        max_people: attraction.max_people,
        max_ready_waiting: attraction.max_ready_waiting,
      },
      inside: peopleInside(attraction.id),
      waiting: db.entries.filter((e) => e.attraction_id === attraction.id && !e.is_ready).length,
      ready: db.entries
        .filter((e) => e.attraction_id === attraction.id && e.is_ready)
        .map((entry) => {
          const billet = billetOf(entry.billet_id)
          return {
            id: entry.id,
            username: db.users.find((u) => u.id === billet.user_id)?.username ?? '—',
            billet: publicBillet(billet),
            ready_at: entry.ready_at,
            ready_expired: readyExpired(entry),
          }
        }),
    }))
  },

  // L'admin fait entrer le visiteur. Contrairement à la validation côté
  // visiteur, une place au délai dépassé peut être acceptée : c'est le sens du
  // poste, l'admin décide en sachant que le visiteur s'est fait attendre.
  async acceptEntry(entryId) {
    await wait()
    const entry = db.entries.find((e) => e.id === entryId)
    if (!entry) fail("Cette place n'existe plus.")
    db.visits.push({
      id: nextId(),
      attraction_id: entry.attraction_id,
      billet_id: entry.billet_id,
      entered_at: new Date().toISOString(),
    })
    db.entries = db.entries.filter((e) => e.id !== entryId)
    return null
  },

  // L'admin retire la place : le visiteur n'entre pas, et sa place est rendue.
  async refuseEntry(entryId) {
    return mock.leaveQueue(entryId)
  },
}
