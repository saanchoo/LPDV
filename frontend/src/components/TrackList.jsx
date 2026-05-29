function TrackList({ tracks, title, onRemove }) {
  return (
    <div>
      {title && <p className="track-list-title">{title}</p>}
      <div className="track-list">
        {tracks.map((track, i) => (
          <div key={track.id + i} className="track-item">
            <span className="track-num">{i + 1}</span>
            {track.image
              ? <img src={track.image} alt={track.name} className="track-img" />
              : <div className="track-img" style={{ background: 'var(--bg-elevated)' }} />
            }
            <div className="track-info">
              <div className="track-name">{track.name}</div>
              <div className="track-artist">{track.artist}</div>
            </div>
            {onRemove && (
              <button
                className="track-remove"
                onClick={() => onRemove(track.id)}
                title="Eliminar de la playlist"
              >×</button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default TrackList
