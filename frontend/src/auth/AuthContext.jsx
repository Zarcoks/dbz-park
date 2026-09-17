/**
 * Qui est connecté — une information dont toutes les pages ont besoin.
 *
 * Plutôt que de la faire descendre de composant en composant, on la pose une
 * fois ici et chaque page la lit avec `useAuth()`. C'est l'équivalent React du
 * `{{ user }}` que Django donnait à tous les templates.
 */
import { createContext, useContext, useEffect, useState } from 'react'

import * as authApi from '../api/auth'
import { getToken, setToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // Tant qu'on n'a pas fini de vérifier le jeton, on ne sait pas encore si le
  // visiteur est connecté : sans cet état, on le renverrait à tort vers la
  // page de connexion à chaque rechargement.
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => {
        // Jeton périmé ou invalide : on le jette, sinon on le repropose en
        // vain à chaque rechargement.
        setToken(null)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const value = {
    user,
    loading,
    login: async (credentials) => setUser(await authApi.login(credentials)),
    signup: async (form) => setUser(await authApi.signup(form)),
    logout: async () => {
      await authApi.logout()
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un <AuthProvider>.')
  }
  return context
}
