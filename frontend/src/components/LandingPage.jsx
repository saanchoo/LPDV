import logo from '../assets/logo.png'

function LandingPage() {
  const handleLogin = () => {
    window.location.href = '/api/auth/login'
  }

  return (
    <div className="landing">
      <div className="landing-inner">
        <img src={logo} alt="La Playlist Del Vago" style={{ maxWidth: '340px', width: '80%', marginBottom: '1.5rem' }} />
        <h1>La Playlist Del Vago</h1>
        <p className="landing-tagline">
          Conecta tu Spotify, nosotros analizamos lo que escuchas<br />
          y generamos una playlist perfecta para ti.
        </p>

        <div className="landing-features">
          <span className="landing-feature">Basada en tu historial real</span>
          <span className="landing-feature">Recomendaciones de Spotify</span>
          <span className="landing-feature">Se crea en tu cuenta</span>
        </div>

        <button className="btn-green" onClick={handleLogin}>
          Iniciar sesión con Spotify
        </button>
      </div>
    </div>
  )
}

export default LandingPage
