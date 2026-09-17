/** Une pastille de fait : le monde présent, la durée d'un tour, la tolérance. */
export default function CapacityBadge({ icon, children }) {
  return (
    <span className="capacity-badge">
      <i className={`bi ${icon}`} />
      {children}
    </span>
  )
}
