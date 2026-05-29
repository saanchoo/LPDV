import { useState } from 'react'
import GeneratorForm from './GeneratorForm'
import TrackPreview from './TrackPreview'
import ResultCard from './ResultCard'
import HistoryPanel from './HistoryPanel'

function Dashboard({ user }) {
  const [step, setStep] = useState('form')
  const [recommendations, setRecommendations] = useState([])
  const [seedTracks, setSeedTracks] = useState([])
  const [playlistUrl, setPlaylistUrl] = useState('')
  const [playlistName, setPlaylistName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [historyKey, setHistoryKey] = useState(0)

  // seedTracks: array de track objects seleccionados por el usuario (1-5)
  // numSongs: cuántas canciones tendrá la playlist (10-50)
  const handleGenerate = (seedTracks, numSongs) => {
    setLoading(true)
    setError('')
    fetch('/api/playlist/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed_tracks: seedTracks, num_songs: numSongs })
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) throw new Error(data.error)
        setRecommendations(data.recommendations)
        setSeedTracks(data.seed_tracks)
        setStep('preview')
      })
      .catch(err => setError(err.message || 'Error generando recomendaciones'))
      .finally(() => setLoading(false))
  }

  // filteredTracks: la lista tras quitar canciones en el preview
  const handleCreate = (name, filteredTracks) => {
    setLoading(true)
    setError('')
    const uris = (filteredTracks || recommendations).map(t => t.uri)
    fetch('/api/playlist/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, track_uris: uris })
    })
      .then(r => r.json())
      .then(data => {
        if (data.error) throw new Error(data.error)
        setPlaylistUrl(data.playlist_url)
        setPlaylistName(name)
        setStep('done')
        setHistoryKey(k => k + 1)
      })
      .catch(err => setError(err.message || 'Error creando la playlist'))
      .finally(() => setLoading(false))
  }

  const handleReset = () => {
    setStep('form')
    setRecommendations([])
    setSeedTracks([])
    setPlaylistUrl('')
    setError('')
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Hola, {user.name} 👋</h2>
        <p>Elige canciones semilla y genera tu playlist.</p>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {step === 'form' && (
        <GeneratorForm onGenerate={handleGenerate} loading={loading} />
      )}
      {step === 'preview' && (
        <TrackPreview
          seedTracks={seedTracks}
          recommendations={recommendations}
          onConfirm={handleCreate}
          onBack={handleReset}
          loading={loading}
        />
      )}
      {step === 'done' && (
        <ResultCard
          playlistUrl={playlistUrl}
          playlistName={playlistName}
          onReset={handleReset}
        />
      )}

      <HistoryPanel refreshKey={historyKey} />
    </div>
  )
}

export default Dashboard
