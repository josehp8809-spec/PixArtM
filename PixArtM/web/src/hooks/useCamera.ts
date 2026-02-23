/**
 * Custom hook for camera access and photo capture
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export interface CameraError {
    code: string;
    message: string;
}

export interface UseCameraResult {
    videoRef: React.RefObject<HTMLVideoElement>;
    canvasRef: React.RefObject<HTMLCanvasElement>;
    stream: MediaStream | null;
    isStreaming: boolean;
    error: CameraError | null;
    facingMode: 'user' | 'environment';
    hasMultipleCameras: boolean;
    switchCamera: () => void;
    capturePhoto: () => Promise<Blob | null>;
    stopCamera: () => void;
}

export function useCamera(): UseCameraResult {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<CameraError | null>(null);
    const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
    const [hasMultipleCameras, setHasMultipleCameras] = useState(false);

    // Check for multiple cameras
    useEffect(() => {
        const checkCameras = async () => {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                setHasMultipleCameras(videoDevices.length > 1);
            } catch (err) {
                console.error('Error checking cameras:', err);
            }
        };

        checkCameras();
    }, []);

    // Start camera stream
    const startCamera = useCallback(async (mode: 'user' | 'environment') => {
        try {
            setError(null);

            // Stop existing stream
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }

            // Request camera access
            const constraints: MediaStreamConstraints = {
                video: {
                    facingMode: mode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };

            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                videoRef.current.onloadedmetadata = () => {
                    videoRef.current?.play();
                    setIsStreaming(true);
                };
            }

            setStream(mediaStream);
        } catch (err: any) {
            console.error('Error accessing camera:', err);

            let errorMessage = 'No se pudo acceder a la cámara';
            let errorCode = 'UNKNOWN_ERROR';

            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMessage = 'Permiso de cámara denegado. Por favor, permite el acceso a la cámara en la configuración de tu navegador.';
                errorCode = 'PERMISSION_DENIED';
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                errorMessage = 'No se encontró ninguna cámara en este dispositivo.';
                errorCode = 'NO_CAMERA';
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                errorMessage = 'La cámara está siendo usada por otra aplicación.';
                errorCode = 'CAMERA_IN_USE';
            } else if (err.name === 'OverconstrainedError') {
                errorMessage = 'La cámara no cumple con los requisitos necesarios.';
                errorCode = 'CONSTRAINTS_ERROR';
            }

            setError({ code: errorCode, message: errorMessage });
            setIsStreaming(false);
        }
    }, [stream]);

    // Initialize camera on mount
    useEffect(() => {
        startCamera(facingMode);

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [facingMode]);

    // Switch between front and back camera
    const switchCamera = useCallback(() => {
        setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    }, []);

    // Capture photo from video stream
    const capturePhoto = useCallback(async (): Promise<Blob | null> => {
        if (!videoRef.current || !canvasRef.current || !isStreaming) {
            return null;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;

        // Set canvas size to video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            return null;
        }

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to blob
        return new Promise<Blob | null>((resolve) => {
            canvas.toBlob(
                (blob) => resolve(blob),
                'image/jpeg',
                0.95 // High quality for initial capture (will be compressed later)
            );
        });
    }, [isStreaming]);

    // Stop camera
    const stopCamera = useCallback(() => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
            setIsStreaming(false);
        }
    }, [stream]);

    return {
        videoRef,
        canvasRef,
        stream,
        isStreaming,
        error,
        facingMode,
        hasMultipleCameras,
        switchCamera,
        capturePhoto,
        stopCamera
    };
}
