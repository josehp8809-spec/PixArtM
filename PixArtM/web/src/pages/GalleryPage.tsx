/**
 * Gallery Page Component
 * 
 * View and download photos from an event
 * Route: /g/:token
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getEventById, getEventCaptures, generateAlbumZip } from '../services/supabaseService';
import { useGallery } from '../hooks/useGallery';
import LazyImage from '../components/LazyImage';
import { Event, Capture } from '../../../shared/types/index';
import '../styles/GalleryPage.css';

export default function GalleryPage() {
    const { token } = useParams<{ token: string }>();

    const [event, setEvent] = useState<Event | null>(null);
    const [captures, setCaptures] = useState<Capture[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [downloadingZip, setDownloadingZip] = useState(false);

    const gallery = useGallery(captures.length);

    // Load event and captures
    useEffect(() => {
        const loadGallery = async () => {
            if (!token) {
                setError('Token inválido');
                setLoading(false);
                return;
            }

            try {
                // Find event by gallery token
                // Note: In production, you'd have a dedicated endpoint for this
                // For now, we'll need to pass the eventId in the URL or use a Cloud Function

                // TODO: Implement getEventByGalleryToken function
                // For now, assuming token format is eventId
                const eventData = await getEventById(token);

                if (!eventData) {
                    setError('Galería no encontrada');
                    setLoading(false);
                    return;
                }

                // Check if gallery is accessible
                if (eventData.status === 'cleaned') {
                    setError('Esta galería ha sido archivada');
                    setLoading(false);
                    return;
                }

                const now = new Date();
                const galleryExpiresAt = eventData.galleryExpiresAt ? new Date(eventData.galleryExpiresAt) : null;

                if (galleryExpiresAt && now > galleryExpiresAt) {
                    setError('Esta galería ha expirado');
                    setLoading(false);
                    return;
                }

                setEvent(eventData);

                // Load captures
                const capturesData = await getEventCaptures(eventData.id);
                setCaptures(capturesData);
                setLoading(false);

            } catch (err: any) {
                console.error('Error loading gallery:', err);
                setError('Error al cargar la galería');
                setLoading(false);
            }
        };

        loadGallery();
    }, [token]);

    // Handle ZIP download
    const handleDownloadZip = async () => {
        if (!event) return;

        setDownloadingZip(true);
        setError(null);

        try {
            const result = await generateAlbumZip(event.id, event.galleryToken);

            if (result.success && result.downloadUrl) {
                // Open download URL in new tab
                window.open(result.downloadUrl, '_blank');
            } else {
                throw new Error(result.message || 'Error al generar el ZIP');
            }
        } catch (err: any) {
            console.error('Error downloading ZIP:', err);
            setError(err.message || 'Error al descargar el álbum');
        } finally {
            setDownloadingZip(false);
        }
    };

    // Handle individual photo download
    const handleDownloadPhoto = (capture: Capture) => {
        if (capture.storageUrl) {
            const link = document.createElement('a');
            link.href = capture.storageUrl;
            link.download = `photo_${String(capture.captureNumber).padStart(4, '0')}.jpg`;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="gallery-page loading">
                <div className="spinner"></div>
                <p>Cargando galería...</p>
            </div>
        );
    }

    // Error state
    if (error && !event) {
        return (
            <div className="gallery-page error">
                <div className="error-icon">🖼️</div>
                <h2>{error}</h2>
                <p>Por favor, verifica el enlace e intenta nuevamente.</p>
            </div>
        );
    }

    // Empty gallery
    if (captures.length === 0) {
        return (
            <div className="gallery-page empty">
                <div className="empty-icon">📸</div>
                <h2>{event?.name}</h2>
                <p>Aún no hay fotos en esta galería</p>
                <p className="empty-hint">Las fotos aparecerán aquí cuando se capturen</p>
            </div>
        );
    }

    return (
        <div className="gallery-page">
            {/* Header */}
            <header className="gallery-header">
                <div className="header-content">
                    <h1>{event?.name}</h1>
                    <p className="photo-count">{captures.length} {captures.length === 1 ? 'foto' : 'fotos'}</p>
                </div>

                {event?.hasCloudAlbum && (
                    <button
                        className="download-all-btn"
                        onClick={handleDownloadZip}
                        disabled={downloadingZip}
                    >
                        {downloadingZip ? (
                            <>
                                <div className="btn-spinner"></div>
                                Generando ZIP...
                            </>
                        ) : (
                            <>
                                📦 Descargar álbum
                            </>
                        )}
                    </button>
                )}
            </header>

            {/* Error message */}
            {error && (
                <div className="error-banner">
                    {error}
                </div>
            )}

            {/* Gallery grid */}
            <div className="gallery-grid">
                {captures.map((capture, index) => (
                    <div key={capture.id} className="gallery-item">
                        <LazyImage
                            src={capture.storageUrl || ''}
                            alt={`Foto ${capture.captureNumber}`}
                            onClick={() => gallery.selectImage(index)}
                            className="gallery-thumbnail"
                        />
                        <div className="gallery-item-overlay">
                            <span className="photo-number">#{capture.captureNumber}</span>
                            <button
                                className="download-single-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDownloadPhoto(capture);
                                }}
                                aria-label="Descargar foto"
                            >
                                ⬇️
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Lightbox */}
            {gallery.selectedImage !== null && (
                <div className="lightbox" onClick={gallery.closeImage}>
                    <button className="lightbox-close" onClick={gallery.closeImage}>
                        ✕
                    </button>

                    <button
                        className="lightbox-nav lightbox-prev"
                        onClick={(e) => {
                            e.stopPropagation();
                            gallery.prevImage();
                        }}
                    >
                        ‹
                    </button>

                    <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
                        {gallery.selectedImage !== null && (
                            <>
                                <img
                                    src={captures[gallery.selectedImage].storageUrl || ''}
                                    alt={`Foto ${captures[gallery.selectedImage].captureNumber}`}
                                    className="lightbox-image"
                                />
                                <div className="lightbox-info">
                                    <span className="lightbox-counter">
                                        {gallery.selectedImage + 1} / {captures.length}
                                    </span>
                                    <button
                                        className="lightbox-download"
                                        onClick={() => handleDownloadPhoto(captures[gallery.selectedImage!])}
                                    >
                                        ⬇️ Descargar
                                    </button>
                                </div>
                            </>
                        )}
                    </div>

                    <button
                        className="lightbox-nav lightbox-next"
                        onClick={(e) => {
                            e.stopPropagation();
                            gallery.nextImage();
                        }}
                    >
                        ›
                    </button>
                </div>
            )}

            {/* Footer */}
            <footer className="gallery-footer">
                <p>PixArtM © {new Date().getFullYear()}</p>
                {event?.galleryExpiresAt && (
                    <p className="expiry-notice">
                        Galería disponible hasta {new Date(event.galleryExpiresAt).toLocaleDateString()}
                    </p>
                )}
            </footer>
        </div>
    );
}
