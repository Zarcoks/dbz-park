/** Les billets du visiteur, et l'assignation d'un numéro reçu par mail. */
import { api } from './client'
import { endpoints } from './endpoints'
import { USE_MOCK, mock } from './mock'

export function listBillets() {
  return USE_MOCK ? mock.billets() : api.get(endpoints.billets)
}

export function assignBillet(numero) {
  return USE_MOCK ? mock.assignBillet({ numero }) : api.post(endpoints.assignBillet, { numero })
}
