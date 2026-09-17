/**
 * La porte d'une page réservée — l'équivalent de `LoginRequiredMixin` et de
 * `StaffOnlyMixin` côté Django.
 *
 * `staffOnly` ferme la page aux visiteurs ordinaires : ils reçoivent le même
 * refus que le 403 de la console.
 */
import { Navigate } from 'react-router-dom'

import { useAuth } from './AuthContext'

export default function RequireAuth({ staffOnly = false, children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <p className="empty-state">Chargement…</p>
  }

  if (!user) {
    return <Navigate to="/connexion" replace />
  }

  if (staffOnly && !user.is_staff) {
    return (
      <div className="park-card">
        <div className="empty-state">
          <i className="bi bi-shield-lock" />
          Cette page est réservée à l'équipe du parc.
        </div>
      </div>
    )
  }

  return children
}
