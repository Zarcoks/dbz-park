/**
 * LA liste des adresses de l'API. Un seul fichier à corriger le jour où le back
 * nomme ses routes autrement : rien d'autre dans le front ne connaît une URL.
 *
 * Chaque entrée reprend une vue Django existante — la colonne de droite dit
 * laquelle, pour que la correspondance reste lisible des deux côtés.
 */

export const endpoints = {
  // ── Comptes ────────────────────────────────  park_management/pages/accounts/
  signup: '/auth/inscription/', //  POST   SignupView
  login: '/auth/connexion/', //     POST   LoginView
  logout: '/auth/deconnexion/', //  POST   LogoutView
  me: '/auth/moi/', //              GET    (nouveau : qui est connecté)

  // ── Billets ────────────────────────────────  park_management/pages/tickets/
  billets: '/billets/', //          GET    TicketList
  assignBillet: '/billets/assigner/', // POST AssignTicket

  // ── Attractions & files ────────────────────  park_management/pages/attractions/
  attractions: '/attractions/', //  GET    AttractionList
  joinQueue: (attractionId) => `/attractions/${attractionId}/file/rejoindre/`, // POST QueueJoin
  leaveQueue: (entryId) => `/files/${entryId}/quitter/`, //   POST QueueLeave
  validateQueue: (entryId) => `/files/${entryId}/valider/`, // POST QueueValidate

  // ── Console admin ──────────────────────────  park_management/pages/console/
  console: '/console/', //          GET    ConsoleView
  acceptEntry: (entryId) => `/console/places/${entryId}/accepter/`, // POST AcceptEntry
  refuseEntry: (entryId) => `/console/places/${entryId}/refuser/`, //  POST RefuseEntry
}
