/**
 * Main App Component
 * Handles routing for camera and gallery pages
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CameraPage from './pages/CameraPage';
import GalleryPage from './pages/GalleryPage';
import './styles/App.css';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Camera capture page */}
                <Route path="/e/:slug" element={<CameraPage />} />

                {/* Gallery page */}
                <Route path="/g/:token" element={<GalleryPage />} />

                {/* Home redirect */}
                <Route path="/" element={
                    <div className="home-page">
                        <h1>PixArtM</h1>
                        <p>Escanea el código QR del evento para comenzar</p>
                    </div>
                } />

                {/* 404 */}
                <Route path="*" element={
                    <div className="error-page">
                        <h1>404</h1>
                        <p>Página no encontrada</p>
                    </div>
                } />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
