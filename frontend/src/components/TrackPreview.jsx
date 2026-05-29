import { useState } from 'react'
import TrackList from './TrackList'

function TrackPreview({ seedTracks, recommendations: initialRecs, onConfirm, onBack, loading }) {
  const [name, setName] = useState('Playlist del Vago')
  const [recs, setRecs] = useState(initialRecs)

  const removeTrack = (id) => {
    setRecs(prev => prev.filter(t => t.id !== id))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (name.trim() && recs.length > 0) onConfirm(name.trim(), recs)
  }

  return (
    <div>
      <div className="preview-grid">
        <div className="preview-panel">
          <TrackList tracks={seedTracks} title={`Semillas (${seedTracks.length})`} />
        </div>
        <div className="preview-panel">
          <TrackList
            tracks={recs}
            title={`Recomendaciones (${recs.length}) — click × para eliminar`}
            onRemove={removeTrack}
          />
        </div>
      </div>

      <div className="preview-actions">
        <p className="preview-actions-title">
          {recs.length === 0
            ? 'No quedan canciones — vuelve y genera de nuevo.'
            : `${recs.length} canciones listas. Dale un nombre y créala.`}
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Nombre de la playlist..."
              className="form-input"
              maxLength={100}
              required
              disabled={recs.length === 0}
            />
          </div>
          <div className="preview-btn-row">
            <button
              type="submit"
              className="btn-green"
              disabled={loading || !name.trim() || recs.length === 0}
            >
              {loading ? 'Creando...' : `Crear playlist (${recs.length} canciones)`}
            </button>
            <button type="button" className="btn-outline" onClick={onBack} disabled={loading}>
              Volver
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TrackPreview
