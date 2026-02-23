/**
 * Camera Page Component
 * 
 * Main page for photo capture at events
 * Route: /e/:slug
 */

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useCamera } from '../hooks/useCamera';
import { getEventBySlug, reserveCapture, uploadPhoto, isEventActive, hasReachedLimit, getRemainingPhotos } from '../services/firebaseService';
import { compressImage, applyFrameOverlay, downloadToDevice } from '../utils/imageProcessing';
import { Event } from '../../../shared/types/index';
import CameraFallback from '../components/CameraFallback';
import '../styles/CameraPage.css';

export default function CameraPage() {
    const { slug } = useParams<{ slug: string }>();
    const camera = useCamera();

    const [event, setEvent] = useState<Event | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [capturing, setCapturing] = useState(false);
    const [countdown, setCountdown] = useState<number | null>(null);
    const [lastPhoto, setLastPhoto] = useState<string | null>(null);
    const [uploadProgress, setUploadProgress] = useState<string | null>(null);

    // Load event data
    useEffect(() => {
        const loadEvent = async () => {
            if (!slug) {
                setError('URL inválida');
                setLoading(false);
                return;
            }

            try {
                const eventData = await getEventBySlug(slug);

                if (!eventData) {
                    setError('Evento no encontrado');
                    setLoading(false);
                    return;
                }

                setEvent(eventData);
                setLoading(false);
            } catch (err: any) {
                console.error('Error loading event:', err);
                setError('Error al cargar el evento');
                setLoading(false);
            }
        };

        loadEvent();
    }, [slug]);

    // Handle photo capture
    const handleCapture = async () => {
        if (!event || !camera.isStreaming || capturing) {
            return;
        }

        // Validate event status
        if (!isEventActive(event)) {
            setError('El evento no está activo');
            return;
        }

        if (hasReachedLimit(event)) {
            setError('Se ha alcanzado el límite de fotos');
            return;
        }

        setCapturing(true);
        setError(null);

        try {
            // Countdown timer (3 seconds)
            for (let i = 3; i > 0; i--) {
                setCountdown(i);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            setCountdown(null);

            // Capture photo
            const photoBlob = await camera.capturePhoto();
            if (!photoBlob) {
                throw new Error('No se pudo capturar la foto');
            }

            setUploadProgress('Comprimiendo imagen...');

            // Compress image
            const compressed = await compressImage(photoBlob);
            console.log(`Compresión: ${compressed.originalSize} → ${compressed.compressedSize} bytes (${compressed.compressionRatio.toFixed(2)}x)`);

            // Apply frame overlay if available
            let finalBlob = compressed.blob;
            if (event.frameDesign?.overlayUrl) {
                setUploadProgress('Aplicando marco...');
                finalBlob = await applyFrameOverlay(compressed.blob, event.frameDesign.overlayUrl);
            }

            // Save to device (always)
            setUploadProgress('Guardando en dispositivo...');
            const filename = `${event.slug}_${Date.now()}.jpg`;
            downloadToDevice(finalBlob, filename);

            // Show preview
            const previewUrl = URL.createObjectURL(finalBlob);
            setLastPhoto(previewUrl);

            // Reserve capture slot
            setUploadProgress('Reservando espacio...');
            const reservation = await reserveCapture(event.id);

            if (!reservation.success) {
                throw new Error(reservation.message || 'No se pudo reservar el espacio');
            }

            // Upload to cloud if event has cloud album
            if (event.hasCloudAlbum && reservation.captureNumber) {
                setUploadProgress('Subiendo a la nube...');
                await uploadPhoto(event.id, reservation.captureNumber, finalBlob);
            }

            // Update event state
            if (reservation.event) {
                setEvent(prev => prev ? {
                    ...prev,
                    captureCount: reservation.event!.captureCount,
                    status: reservation.event!.status
                } : null);
            }

            setUploadProgress('¡Foto guardada!');
            setTimeout(() => setUploadProgress(null), 3000);

        } catch (err: any) {
            console.error('Error capturing photo:', err);
            setError(err.message || 'Error al capturar la foto');
        } finally {
            setCapturing(false);
            setCountdown(null);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="camera-page loading">
                <div className="spinner"></div>
                <p>Cargando evento...</p>
            </div>
        );
    }

    // Error state
    if (error && !event) {
        return (
            <div className="camera-page error">
                <div className="error-icon">⚠️</div>
                <h2>{error}</h2>
                <p>Por favor, verifica el enlace e intenta nuevamente.</p>
            </div>
        );
    }

    // Camera error fallback
    if (camera.error) {
        return <CameraFallback error={camera.error} eventName={event?.name || ''} />;
    }

    return (
        <div className="camera-page">
            {/* Header */}
            <header className="camera-header">
                <h1>{event?.name}</h1>
                <div className="photo-counter">
                    <span className="count">{event?.captureCount || 0}</span>
                    <span className="separator">/</span>
                    <span className="limit">{event?.photoLimit || 0}</span>
                </div>
            </header>

            {/* Camera viewport */}
            <div className="camera-viewport">
                <video
                    ref={camera.videoRef}
                    autoPlay
                    playsInline
                    muted
                    className={`camera-video ${!camera.isStreaming ? 'hidden' : ''}`}
                />
                <canvas ref={camera.canvasRef} className="camera-canvas hidden" />

                {/* Countdown overlay */}
                {countdown !== null && (
                    <div className="countdown-overlay">
                        <div className="countdown-number">{countdown}</div>
                    </div>
                )}

                {/* Last photo preview */}
                {lastPhoto && !capturing && (
                    <div className="photo-preview">
                        <img src={lastPhoto} alt="Última foto" />
                    </div>
                )}

                {/* Upload progress */}
                {uploadProgress && (
                    <div className="upload-progress">
                        <div className="progress-spinner"></div>
                        <p>{uploadProgress}</p>
                    </div>
                )}
            </div>

            {/* Controls */}
            <div className="camera-controls">
                {/* Switch camera button */}
                {camera.hasMultipleCameras && (
                    <button
                        className="control-btn switch-camera"
                        onClick={camera.switchCamera}
                        disabled={capturing}
                        aria-label="Cambiar cámara"
                    >
                        🔄
                    </button>
                )}

                {/* Capture button */}
                <button
                    className={`capture-btn ${capturing ? 'capturing' : ''}`}
                    onClick={handleCapture}
                    disabled={capturing || !camera.isStreaming || !event || !isEventActive(event) || hasReachedLimit(event)}
                    aria-label="Tomar foto"
                >
                    <div className="capture-btn-inner"></div>
                </button>

                {/* Info button */}
                <button
                    className="control-btn info"
                    onClick={() => alert(`Fotos restantes: ${getRemainingPhotos(event!)}`)}
                    disabled={capturing}
                    aria-label="Información"
                >
                    ℹ️
                </button>
            </div>

            {/* Status message */}
            {error && (
                <div className="status-message error">
                    {error}
                </div>
            )}

            {event && !isEventActive(event) && (
                <div className="status-message warning">
                    Este evento no está activo actualmente
                </div>
            )}

            {event && hasReachedLimit(event) && (
                <div className="status-message warning">
                    Se ha alcanzado el límite de fotos
                </div>
            )}
        </div>
    );
}
