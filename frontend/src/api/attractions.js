/** Le catalogue des attractions et les gestes sur une file. */
import { api } from './client'
import { endpoints } from './endpoints'
import { USE_MOCK, mock } from './mock'

/** Les attractions, avec ce que le visiteur y a en cours (place, présence). */
export function listAttractions() {
  return USE_MOCK ? mock.attractions() : api.get(endpoints.attractions)
}

export function joinQueue(attractionId) {
  return USE_MOCK ? mock.joinQueue(attractionId) : api.post(endpoints.joinQueue(attractionId))
}

/**
 * Le rang d'une place, recalculé à la volée. Le front l'interroge seul, sans
 * recharger toute la liste des attractions : c'est ce qui permet de rafraîchir
 * l'attente toutes les quelques secondes sans faire travailler le back pour rien.
 */
export function queuePosition(entryId) {
  return USE_MOCK ? mock.queuePosition(entryId) : api.get(endpoints.queuePosition(entryId))
}

export function leaveQueue(entryId) {
  return USE_MOCK ? mock.leaveQueue(entryId) : api.post(endpoints.leaveQueue(entryId))
}

export function validateQueue(entryId) {
  return USE_MOCK ? mock.validateQueue(entryId) : api.post(endpoints.validateQueue(entryId))
}
