/**
 * Lazy Loaded Image Component
 * Uses intersection observer for performance
 */

import { useLazyLoad } from '../hooks/useGallery';
import '../styles/LazyImage.css';

interface LazyImageProps {
    src: string;
    alt: string;
    onClick?: () => void;
    className?: string;
}

export default function LazyImage({ src, alt, onClick, className = '' }: LazyImageProps) {
    const { imageRef, isLoaded, isInView } = useLazyLoad();

    return (
        <div className={`lazy-image-container ${className}`} onClick={onClick}>
            <img
                ref={imageRef}
                src={isInView ? src : undefined}
                alt={alt}
                className={`lazy-image ${isLoaded ? 'loaded' : 'loading'}`}
                loading="lazy"
            />
            {!isLoaded && (
                <div className="lazy-image-placeholder">
                    <div className="lazy-image-spinner"></div>
                </div>
            )}
        </div>
    );
}
