import { useState, useEffect } from 'react'

function TrackRow({ track, selected, disabled, onToggle }) {
  return (
    <div
      className={`seed-item ${selected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={() => !disabled && onToggle(track)}
    >
      {track.image
        ? <img src={track.image} alt="" className="track-img" />
        : <div className="track-img" style={{ background: 'var(--bg-elevated)' }} />
      }
      <div className="track-info">
        <div className="track-name">{track.name}</div>
        <div className="track-artist">{track.artist}</div>
      </div>
      <div className="seed-check">{selected ? '✓' : '+'}</div>
    </div>
  )
}

function GeneratorForm({ onGenerate, loading }) {
  const [mode, setMode] = useState('recent')       // 'recent' | 'search'
  const [selectedSeeds, setSelectedSeeds] = useState([])  // max 5
  const [numSongs, setNumSongs] = useState(20)

  // Recent tracks
  const [recentTracks, setRecentTracks] = useState([])
  const [loadingRecent, setLoadingRecent] = useState(false)

  // Search
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    setLoadingRecent(true)
    fetch('/api/tracks/recent')
      .then(r => r.json())
      .then(data => setRecentTracks(data.tracks || []))
      .catch(() => {})
      .finally(() => setLoadingRecent(false))
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    fetch(`/api/tracks/search?q=${encodeURIComponent(query.trim())}`)
      .then(r => r.json())
      .then(data => setSearchResults(data.tracks || []))
      .catch(() => {})
      .finally(() => setSearching(false))
  }

  const isSelected = (id) => selectedSeeds.some(t => t.id === id)

  const toggleTrack = (track) => {
    if (isSelected(track.id)) {
      setSelectedSeeds(prev => prev.filter(t => t.id !== track.id))
    } else {
      if (selectedSeeds.length >= 5) return
      setSelectedSeeds(prev => [...prev, track])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (selectedSeeds.length === 0 || loading) return
    onGenerate(selectedSeeds, numSongs)
  }

  const maxReached = selectedSeeds.length >= 5

  return (
    <form onSubmit={handleSubmit}>

      {/* ── PASO 1: Semillas ─────────────────────────────── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <p className="step-label">Paso 1 — Canciones semilla ({selectedSeeds.length}/5)</p>

        <div className="tab-switcher">
          <button type="button"
            className={`tab-btn ${mode === 'recent' ? 'active' : ''}`}
            onClick={() => setMode('recent')}>
            Últimas escuchadas
          </button>
          <button type="button"
            className={`tab-btn ${mode === 'search' ? 'active' : ''}`}
            onClick={() => setMode('search')}>
            Buscar canciones
          </button>
        </div>

        {/* Recientes */}
        {mode === 'recent' && (
          <div className="seed-list">
            {loadingRecent
              ? <p style={{ color: 'var(--text-dim)', padding: '12px 0' }}>Cargando historial...</p>
              : recentTracks.map((track, i) => (
                <TrackRow
                  key={track.id + i}
                  track={track}
                  selected={isSelected(track.id)}
                  disabled={maxReached && !isSelected(track.id)}
                  onToggle={toggleTrack}
                />
              ))
            }
          </div>
        )}

        {/* Búsqueda */}
        {mode === 'search' && (
          <>
            <div className="search-row">
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') handleSearch(e) }}
                placeholder="Nombre de canción o artista..."
                className="form-input"
              />
              <button type="button" className="btn-green" onClick={handleSearch} disabled={searching}>
                {searching ? '...' : 'Buscar'}
              </button>
            </div>
            <div className="seed-list">
              {searchResults.length === 0 && !searching && (
                <p style={{ color: 'var(--text-dim)', padding: '8px 0', fontSize: 13 }}>
                  Escribe algo y pulsa Buscar.
                </p>
              )}
              {searchResults.map((track, i) => (
                <TrackRow
                  key={track.id + i}
                  track={track}
                  selected={isSelected(track.id)}
                  disabled={maxReached && !isSelected(track.id)}
                  onToggle={toggleTrack}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* ── Semillas seleccionadas (chips) ───────────────── */}
      {selectedSeeds.length > 0 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <p className="step-label">Semillas seleccionadas</p>
          <div className="seeds-chips">
            {selectedSeeds.map(track => (
              <div key={track.id} className="seed-chip">
                <span>{track.name} — {track.artist}</span>
                <button type="button" className="seed-chip-remove" onClick={() => toggleTrack(track)}>×</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── PASO 2: Tamaño ───────────────────────────────── */}
      {selectedSeeds.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <p className="step-label">Paso 2 — Tamaño de la playlist</p>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              <span>Canciones a generar</span>
              <span className="form-label-value">{numSongs}</span>
            </label>
            <div className="slider-wrap">
              <input
                type="range"
                min="10"
                max="50"
                value={numSongs}
                onChange={e => setNumSongs(Number(e.target.value))}
                className="slider"
              />
              <div className="slider-labels">
                <span>10 canciones</span>
                <span>50 canciones</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Botón generar ────────────────────────────────── */}
      {selectedSeeds.length > 0 && (
        <button type="submit" className="btn-green" disabled={loading}>
          {loading ? 'Generando...' : `Generar playlist de ${numSongs} canciones`}
        </button>
      )}
    </form>
  )
}

export default GeneratorForm
