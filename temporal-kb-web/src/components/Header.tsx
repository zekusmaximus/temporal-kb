import { Link } from 'react-router-dom'
import './Header.css'

export default function Header() {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <h1 className="site-title">
            <Link to="/">Temporal Knowledge Base</Link>
          </h1>
          <nav className="nav">
            <Link to="/">Home</Link>
            <Link to="/search">Search</Link>
            <Link to="/create">Create Entry</Link>
            <Link to="/timeline">Timeline</Link>
            <Link to="/discover">Discover</Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
