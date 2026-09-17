/**
 * La pastille d'un rôle de billet. Sa couleur vient de la classe
 * `role-badge-<role>` posée dans dbz-park.css : chaque rôle se lit sans son
 * libellé.
 */
export default function RoleBadge({ billet, withIcon = true }) {
  return (
    <span className={`role-badge role-badge-${billet.role}`}>
      {withIcon && <i className="bi bi-stars" />}
      {billet.role_display}
    </span>
  )
}
