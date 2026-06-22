import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import GeneratorPage from './pages/GeneratorPage';
import GalleryPage from './pages/GalleryPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <NavLink to="/" className="app-logo">
            AI.Canvas
          </NavLink>
          <nav className="nav-links">
            <NavLink 
              to="/" 
              className={({isActive}) => isActive ? "nav-link active" : "nav-link"}
              end
            >
              Generate
            </NavLink>
            <NavLink 
              to="/gallery" 
              className={({isActive}) => isActive ? "nav-link active" : "nav-link"}
            >
              Gallery
            </NavLink>
          </nav>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<GeneratorPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
