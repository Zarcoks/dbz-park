/** La création de compte. Reprend `accounts/signup.html`. */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Alert from '../components/Alert'
import { useAuth } from '../auth/AuthContext'

export default function SignupPage() {
  const { signup } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '',
    email: '',
    password1: '',
    password2: '',
  })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    // Les deux mots de passe se vérifient ici, sans aller-retour réseau. Le
    // back refait le contrôle de son côté : ce qui est vérifié dans le
    // navigateur ne protège rien, cela évite seulement un appel pour rien.
    if (form.password1 !== form.password2) {
      setError('Les deux mots de passe ne correspondent pas.')
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      await signup(form)
      navigate('/')
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
          <i className="bi bi-person-plus" /> Créer un compte
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
            <label className="form-label" htmlFor="email">
              Adresse e-mail
            </label>
            <input
              id="email"
              name="email"
              type="email"
              className="form-control"
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
            />
            <div className="helptext">Le numéro de votre billet y est envoyé.</div>
          </div>

          <div className="mb-3">
            <label className="form-label" htmlFor="password1">
              Mot de passe
            </label>
            <input
              id="password1"
              name="password1"
              type="password"
              className="form-control"
              value={form.password1}
              onChange={handleChange}
              autoComplete="new-password"
            />
            <div className="helptext">Au moins 8 caractères, pas seulement des chiffres.</div>
          </div>

          <div className="mb-3">
            <label className="form-label" htmlFor="password2">
              Confirmation du mot de passe
            </label>
            <input
              id="password2"
              name="password2"
              type="password"
              className="form-control"
              value={form.password2}
              onChange={handleChange}
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="btn btn-park w-100" disabled={submitting}>
            {submitting ? 'Création…' : 'Créer mon compte'}
          </button>
        </form>

        <p className="text-center small mt-3 mb-0">
          Déjà inscrit ? <Link to="/connexion">Se connecter</Link>
        </p>
      </div>
    </div>
  )
}
