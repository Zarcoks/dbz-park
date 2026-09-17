/** Le catalogue des attractions et les trois gestes sur une file. */
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

export function leaveQueue(entryId) {
  return USE_MOCK ? mock.leaveQueue(entryId) : api.post(endpoints.leaveQueue(entryId))
}

export function validateQueue(entryId) {
  return USE_MOCK ? mock.validateQueue(entryId) : api.post(endpoints.validateQueue(entryId))
}
