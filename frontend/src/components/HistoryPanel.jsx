import { useState, useEffect } from 'react'

function HistoryPanel({ refreshKey }) {
  const [playlists, setPlaylists] = useState([])

  useEffect(() => {
    fetch('/api/history')
      .then(r => r.json())
      .then(data => setPlaylists(data.playlists || []))
      .catch(() => {})
  }, [refreshKey])

  if (playlists.length === 0) return null

  const formatDate = (iso) => {
    const d = new Date(iso)
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  return (
    <div className="history-panel">
      <p className="history-title">Playlists creadas ({playlists.length})</p>
      <div className="history-list">
        {playlists.map(p => (
          <div key={p.id} className="history-item">
            <div className="history-item-info">
              <div className="history-item-name">{p.name}</div>
              <div className="history-item-meta">{p.track_count} canciones · {formatDate(p.created_at)}</div>
            </div>
            <a href={p.url} target="_blank" rel="noopener noreferrer" className="history-item-link">
              Abrir ↗
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HistoryPanel
