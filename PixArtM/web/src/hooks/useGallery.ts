/**
 * Custom hook for lazy loading gallery images
 * Implements intersection observer for performance
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export interface LazyImageProps {
    src: string;
    alt: string;
    onLoad?: () => void;
}

export interface UseLazyLoadResult {
    imageRef: React.RefObject<HTMLImageElement>;
    isLoaded: boolean;
    isInView: boolean;
}

export function useLazyLoad(): UseLazyLoadResult {
    const imageRef = useRef<HTMLImageElement>(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [isInView, setIsInView] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setIsInView(true);
                        observer.disconnect();
                    }
                });
            },
            {
                rootMargin: '50px', // Start loading 50px before entering viewport
                threshold: 0.01
            }
        );

        if (imageRef.current) {
            observer.observe(imageRef.current);
        }

        return () => {
            observer.disconnect();
        };
    }, []);

    const handleLoad = useCallback(() => {
        setIsLoaded(true);
    }, []);

    useEffect(() => {
        const img = imageRef.current;
        if (img && isInView) {
            img.addEventListener('load', handleLoad);
            return () => {
                img.removeEventListener('load', handleLoad);
            };
        }
    }, [isInView, handleLoad]);

    return {
        imageRef,
        isLoaded,
        isInView
    };
}

/**
 * Hook for managing gallery state
 */
export interface UseGalleryResult {
    selectedImage: number | null;
    selectImage: (index: number) => void;
    closeImage: () => void;
    nextImage: () => void;
    prevImage: () => void;
}

export function useGallery(totalImages: number): UseGalleryResult {
    const [selectedImage, setSelectedImage] = useState<number | null>(null);

    const selectImage = useCallback((index: number) => {
        setSelectedImage(index);
    }, []);

    const closeImage = useCallback(() => {
        setSelectedImage(null);
    }, []);

    const nextImage = useCallback(() => {
        setSelectedImage((prev) => {
            if (prev === null) return null;
            return (prev + 1) % totalImages;
        });
    }, [totalImages]);

    const prevImage = useCallback(() => {
        setSelectedImage((prev) => {
            if (prev === null) return null;
            return prev === 0 ? totalImages - 1 : prev - 1;
        });
    }, [totalImages]);

    // Keyboard navigation
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (selectedImage === null) return;

            switch (e.key) {
                case 'Escape':
                    closeImage();
                    break;
                case 'ArrowRight':
                    nextImage();
                    break;
                case 'ArrowLeft':
                    prevImage();
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedImage, closeImage, nextImage, prevImage]);

    return {
        selectedImage,
        selectImage,
        closeImage,
        nextImage,
        prevImage
    };
}
