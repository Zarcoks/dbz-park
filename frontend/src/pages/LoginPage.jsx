/** La page de connexion. Reprend `accounts/login.html`. */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Alert from '../components/Alert'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  // Un seul gestionnaire pour tous les champs : c'est le `name` de l'input qui
  // dit quelle clé du formulaire changer.
  function handleChange(event) {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login(form)
      navigate('/') // une fois connecté, on arrive sur ses billets
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-column">
      <div className="park-card">
        <h2>
          <i className="bi bi-box-arrow-in-right" /> Connexion
        </h2>

        <Alert message={error} type="error" />

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-3">
            <label className="form-label" htmlFor="username">
              Nom d'utilisateur
            </label>
            <input
              id="username"
              name="username"
              className="form-control"
              value={form.username}
              onChange={handleChange}
              autoComplete="username"
            />
          </div>

          <div className="mb-3">
            <label className="form-label" htmlFor="password">
              Mot de passe
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-control"
              value={form.password}
              onChange={handleChange}
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn btn-park w-100" disabled={submitting}>
            {submitting ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>

        <p className="text-center small mt-3 mb-0">
          Pas encore de compte ? <Link to="/inscription">Créer un compte</Link>
        </p>
      </div>
    </div>
  )
}
