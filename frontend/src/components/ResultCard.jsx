function ResultCard({ playlistUrl, playlistName, onReset }) {
  return (
    <div className="result-card">
      <span className="result-icon">🎉</span>
      <h2>¡Tu playlist está lista!</h2>
      <p>
        <strong style={{ color: 'var(--text)' }}>{playlistName}</strong> ha sido creada en tu cuenta de Spotify.
      </p>
      <div className="result-btn-row">
        <a href={playlistUrl} target="_blank" rel="noopener noreferrer" className="btn-green"
           style={{ display: 'inline-block', textDecoration: 'none' }}>
          Abrir en Spotify
        </a>
        <button className="btn-outline" onClick={onReset}>
          Crear otra
        </button>
      </div>
    </div>
  )
}

export default ResultCard
