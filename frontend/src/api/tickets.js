/** Les billets du visiteur : les lire, en acheter un, le payer, en rattacher un. */
import { api } from './client'
import { endpoints } from './endpoints'
import { USE_MOCK, mock } from './mock'

export function listTickets() {
  return USE_MOCK ? mock.tickets() : api.get(endpoints.tickets)
}

/**
 * Achète un billet depuis l'application. Le billet existe aussitôt, mais il
 * n'est pas payé : c'est `payTicket` qui le rend utilisable.
 */
export function buyTicket(role) {
  return USE_MOCK ? mock.buyTicket({ role }) : api.post(endpoints.tickets, { role })
}

/**
 * Paie un billet acheté juste avant. Les coordonnées bancaires ne font que
 * passer : le front ne les garde nulle part, le back non plus.
 */
export function payTicket(ticketId, card) {
  return USE_MOCK ? mock.payTicket(ticketId, card) : api.post(endpoints.payTicket(ticketId), card)
}

/** Rattache au compte un billet acheté ailleurs (guichet, site), par son numéro. */
export function assignTicket(numero) {
  return USE_MOCK ? mock.assignTicket({ numero }) : api.post(endpoints.assignTicket, { numero })
}
