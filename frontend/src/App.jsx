import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/auth/status')
      .then(r => r.json())
      .then(data => {
        if (data.logged_in) setUser(data.user)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    fetch('/api/auth/logout', { method: 'POST' })
      .then(() => setUser(null))
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
      </div>
    )
  }

  return (
    <>
      <Navbar user={user} onLogout={handleLogout} />
      {user ? <Dashboard user={user} /> : <LandingPage />}
    </>
  )
}

export default App
