/**
 * Le bandeau de retour après une action — ce que faisait le framework
 * `messages` de Django.
 *
 * Il ne s'affiche que s'il y a quelque chose à dire, pour que les pages
 * puissent l'écrire sans condition autour.
 */
export default function Alert({ message, type = 'success' }) {
  if (!message) return null

  return (
    <div className={`alert alert-${type === 'error' ? 'danger' : 'success'} py-2 small`}>
      {message}
    </div>
  )
}
