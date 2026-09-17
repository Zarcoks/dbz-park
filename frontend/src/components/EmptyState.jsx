/** Le bloc « il n'y a rien ici », avec son icône. */
export default function EmptyState({ icon, children }) {
  return (
    <div className="empty-state">
      <i className={`bi ${icon}`} />
      {children}
    </div>
  )
}
