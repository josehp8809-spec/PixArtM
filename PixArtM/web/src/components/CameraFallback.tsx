/**
 * Camera Fallback Component
 * 
 * Displayed when camera access fails (common on iOS Safari)
 * Provides alternative instructions and file upload option
 */

import React, { useState, useRef } from 'react';
import { CameraError } from '../hooks/useCamera';
import '../styles/CameraFallback.css';

interface CameraFallbackProps {
    error: CameraError;
    eventName: string;
}

export default function CameraFallback({ error, eventName }: CameraFallbackProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && file.type.startsWith('image/')) {
            setSelectedFile(file);

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setPreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="camera-fallback">
            <div className="fallback-content">
                {/* Error icon */}
                <div className="error-icon">📷</div>

                {/* Event name */}
                <h1>{eventName}</h1>

                {/* Error message */}
                <div className="error-message">
                    <h2>No se pudo acceder a la cámara</h2>
                    <p>{error.message}</p>
                </div>

                {/* Instructions based on error type */}
                {error.code === 'PERMISSION_DENIED' && (
                    <div className="instructions">
                        <h3>¿Cómo permitir el acceso a la cámara?</h3>
                        <div className="instruction-steps">
                            <div className="step">
                                <span className="step-number">1</span>
                                <p>Toca el ícono de configuración en la barra de direcciones</p>
                            </div>
                            <div className="step">
                                <span className="step-number">2</span>
                                <p>Busca "Cámara" en los permisos</p>
                            </div>
                            <div className="step">
                                <span className="step-number">3</span>
                                <p>Selecciona "Permitir"</p>
                            </div>
                            <div className="step">
                                <span className="step-number">4</span>
                                <p>Recarga esta página</p>
                            </div>
                        </div>
                    </div>
                )}

                {error.code === 'NO_CAMERA' && (
                    <div className="instructions">
                        <p>Este dispositivo no tiene una cámara disponible.</p>
                        <p>Puedes subir una foto desde tu galería:</p>
                    </div>
                )}

                {error.code === 'CAMERA_IN_USE' && (
                    <div className="instructions">
                        <p>La cámara está siendo usada por otra aplicación.</p>
                        <p>Cierra otras aplicaciones que puedan estar usando la cámara e intenta nuevamente.</p>
                    </div>
                )}

                {/* File upload alternative */}
                <div className="upload-alternative">
                    <h3>Alternativa: Sube una foto</h3>
                    <p>Puedes tomar una foto con tu app de cámara y subirla aquí:</p>

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        capture="environment"
                        onChange={handleFileSelect}
                        className="file-input hidden"
                    />

                    <button
                        className="upload-btn"
                        onClick={handleUploadClick}
                    >
                        📸 Seleccionar foto
                    </button>

                    {preview && (
                        <div className="preview-container">
                            <img src={preview} alt="Preview" className="preview-image" />
                            <p className="preview-filename">{selectedFile?.name}</p>
                            <button className="submit-btn">
                                ✓ Subir foto
                            </button>
                        </div>
                    )}
                </div>

                {/* Reload button */}
                <button
                    className="reload-btn"
                    onClick={() => window.location.reload()}
                >
                    🔄 Reintentar
                </button>

                {/* Browser compatibility note */}
                <div className="compatibility-note">
                    <p><strong>Nota:</strong> Para la mejor experiencia, usa Chrome o Firefox en Android, o Safari en iOS.</p>
                </div>
            </div>
        </div>
    );
}
