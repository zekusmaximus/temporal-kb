import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import EntryPage from './pages/EntryPage'
import CreateEntryPage from './pages/CreateEntryPage'
import EditEntryPage from './pages/EditEntryPage'
import TimelinePage from './pages/TimelinePage'
import DiscoverPage from './pages/DiscoverPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main className="container">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/entry/:id" element={<EntryPage />} />
            <Route path="/create" element={<CreateEntryPage />} />
            <Route path="/edit/:id" element={<EditEntryPage />} />
            <Route path="/timeline" element={<TimelinePage />} />
            <Route path="/discover" element={<DiscoverPage />} />
          </Routes>
        </main>
        <footer className="container" style={{ marginTop: '4em', marginBottom: '2em', borderTop: '1px solid var(--border-color)', paddingTop: '1em' }}>
          <p className="text-muted text-small">
            Temporal Knowledge Base - A personal knowledge management system with temporal intelligence
          </p>
        </footer>
      </div>
    </BrowserRouter>
  )
}
