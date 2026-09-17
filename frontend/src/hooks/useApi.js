/**
 * Charger des données depuis l'API, avec les trois états qui vont toujours
 * avec : en cours, en erreur, chargé.
 *
 * Sans ça, chaque page réécrirait le même `useState` × 3 et le même `useEffect`.
 * `reload()` relance l'appel — c'est ce qu'on fait après une action, pour que
 * la page montre l'état d'après.
 *
 *   const { data, loading, error, reload } = useApi(listAttractions)
 */
import { useCallback, useEffect, useState } from 'react'

export function useApi(fetcher) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(() => {
    setLoading(true)
    return fetcher()
      .then((result) => {
        setData(result)
        setError(null)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
    // `fetcher` doit être stable : on passe une fonction importée, pas une
    // fonction recréée à chaque rendu, sinon l'appel repart en boucle.
  }, [fetcher])

  useEffect(() => {
    reload()
  }, [reload])

  return { data, loading, error, reload }
}
