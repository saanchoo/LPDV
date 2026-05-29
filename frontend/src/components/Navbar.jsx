function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-brand-name">LPDV</span>
        <span className="navbar-brand-tagline">La Playlist Del Vago</span>
      </div>

      {user && (
        <div className="navbar-user">
          {user.image
            ? <img src={user.image} alt={user.name} className="navbar-avatar" />
            : <div className="navbar-avatar-placeholder">{user.name?.[0]?.toUpperCase()}</div>
          }
          <span className="navbar-username">{user.name}</span>
          <button className="btn-ghost" onClick={onLogout}>Cerrar sesión</button>
        </div>
      )}
    </nav>
  )
}

export default Navbar
